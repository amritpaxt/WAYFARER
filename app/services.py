from datetime import date, datetime, time
from math import ceil

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import CATEGORY_STAT, RESOURCE_DECAY_PER_MISSED_DAY, REVEAL_QUEST_THRESHOLD, STAT_NAMES
from .models import Character, Episode, Quest, Stat, UnlockedFragment, User


def xp_required_for_next_level(level: int) -> int:
    return ceil(100 * (level ** 1.5))


def character_payload(character: Character) -> dict:
    return {
        "id": character.id,
        "level": character.level,
        "xp": character.xp,
        "xp_to_next_level": xp_required_for_next_level(character.level),
        "resource_meter": character.resource_meter,
        "gold": character.gold,
        "last_login_date": character.last_login_date,
        "stats": {stat.name: stat.value for stat in character.stats},
    }


def apply_login_tick(character: Character) -> int:
    today = date.today()
    missed_days = max((today - character.last_login_date).days, 0)
    if missed_days:
        character.resource_meter = max(0, character.resource_meter - missed_days * RESOURCE_DECAY_PER_MISSED_DAY)
    character.last_login_date = today
    return missed_days


def completed_today_count(db: Session, user_id: int) -> int:
    start = datetime.combine(date.today(), time.min)
    return len(db.scalars(select(Quest).where(Quest.user_id == user_id, Quest.is_completed.is_(True), Quest.completed_at >= start)).all())


def unlock_available_story(db: Session, user: User) -> list[UnlockedFragment]:
    episode = db.scalar(select(Episode).where(Episode.day_number == 1))
    if not episode:
        return []
    completed = completed_today_count(db, user.id)
    existing = {row.fragment_index for row in db.scalars(select(UnlockedFragment).where(UnlockedFragment.user_id == user.id, UnlockedFragment.episode_id == episode.id)).all()}
    eligible = [index for index in range(len(episode.fragments_normal)) if completed >= (index + 1) * 2]
    if completed >= REVEAL_QUEST_THRESHOLD:
        eligible.append(len(episode.fragments_normal))
    made = []
    for index in eligible:
        if index not in existing:
            variant = "hard" if user.character.resource_meter < episode.unlock_resource_threshold else "normal"
            row = UnlockedFragment(user_id=user.id, episode_id=episode.id, fragment_index=index, variant_shown=variant)
            db.add(row)
            made.append(row)
    return made


def complete_quest(db: Session, user: User, quest: Quest) -> list[UnlockedFragment]:
    quest.is_completed = True
    quest.completed_at = datetime.utcnow()
    character = user.character
    character.xp += quest.xp_reward
    character.gold += quest.gold_reward
    character.resource_meter = min(100, character.resource_meter + quest.resource_reward)
    while character.xp >= xp_required_for_next_level(character.level):
        character.xp -= xp_required_for_next_level(character.level)
        character.level += 1
    stat_name = CATEGORY_STAT[quest.category]
    stat = next(stat for stat in character.stats if stat.name == stat_name)
    stat.value += quest.xp_reward
    # Make this completion visible to today's count before checking thresholds.
    db.flush()
    unlocked = unlock_available_story(db, user)
    db.commit()
    return unlocked


def create_user_profile(db: Session, user: User) -> Character:
    character = Character(user=user, last_login_date=date.today())
    character.stats = [Stat(name=name, value=0) for name in STAT_NAMES]
    db.add(character)
    return character
