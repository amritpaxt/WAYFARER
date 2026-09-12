from datetime import date, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.config import REVEAL_QUEST_THRESHOLD, REWARDS
from app.database import Base
from app.models import Episode, Quest, UnlockedFragment, User
from app.seed import STORY, seed
from app.services import (
    advance_story_day,
    apply_login_tick,
    complete_quest,
    create_user_profile,
    ensure_final_vow,
    xp_required_for_next_level,
)


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    seed(session)
    return session


def add_and_complete_case(db, user, number):
    rewards = REWARDS["Easy"]
    quest = Quest(
        user_id=user.id,
        title=f"Case {number}",
        category="Coding/Study",
        difficulty="Easy",
        xp_reward=rewards["xp"],
        gold_reward=rewards["gold"],
        resource_reward=rewards["resource"],
    )
    db.add(quest)
    db.flush()
    return quest, complete_quest(db, user, quest)

def test_xp_curve_increases():
    assert xp_required_for_next_level(1) == 100
    assert xp_required_for_next_level(2) > xp_required_for_next_level(1)

def test_fragment_thresholds_are_ordered():
    assert REVEAL_QUEST_THRESHOLD >= 2 * 3


def test_all_seven_episodes_unlock_their_case_files():
    db = make_session()
    user = User(email="rook@example.com", hashed_password="hash")
    db.add(user)
    db.flush()
    create_user_profile(db, user)
    db.commit()

    assert db.scalars(select(Episode)).all()
    assert len(db.scalars(select(Episode)).all()) == len(STORY) == 7

    for day in range(1, 8):
        assert user.character.day_index == day
        for case_number in range(1, REVEAL_QUEST_THRESHOLD + 1):
            quest, newly_unlocked = add_and_complete_case(db, user, case_number)
            assert quest.story_day == day
            if case_number in {2, 4, 6, 8}:
                assert len(newly_unlocked) == 1

        episode = db.scalar(select(Episode).where(Episode.day_number == day))
        unlocked = db.scalars(
            select(UnlockedFragment)
            .where(
                UnlockedFragment.user_id == user.id,
                UnlockedFragment.episode_id == episode.id,
            )
            .order_by(UnlockedFragment.fragment_index)
        ).all()
        # Three fragments unlock at 2/4/6 closed cases; the reveal unlocks at 8.
        assert [row.fragment_index for row in unlocked] == [0, 1, 2, 3]
        assert {row.variant_shown for row in unlocked} == {"normal"}

        if day < 7:
            assert advance_story_day(user.character) is True
            db.commit()

    ensure_final_vow(db, user)
    db.commit()
    final_vow = db.scalar(
        select(Quest).where(Quest.user_id == user.id, Quest.is_final_vow.is_(True))
    )
    assert final_vow is not None
    assert advance_story_day(user.character) is False


def test_next_episode_unlocks_after_one_calendar_day_and_cases_do_not_carry_over():
    db = make_session()
    user = User(email="calendar@example.com", hashed_password="hash")
    db.add(user)
    db.flush()
    create_user_profile(db, user)
    db.commit()

    for case_number in range(1, 3):
        add_and_complete_case(db, user, case_number)

    user.character.last_login_date = date.today() - timedelta(days=1)
    assert apply_login_tick(user.character) == 1
    assert user.character.day_index == 2

    first_day_cases = db.scalars(
        select(Quest).where(Quest.user_id == user.id, Quest.is_completed.is_(True))
    ).all()
    assert {case.story_day for case in first_day_cases} == {1}

    quest, newly_unlocked = add_and_complete_case(db, user, 3)
    assert quest.story_day == 2
    assert newly_unlocked == []

    _, newly_unlocked = add_and_complete_case(db, user, 4)
    assert [row.fragment_index for row in newly_unlocked] == [0]
