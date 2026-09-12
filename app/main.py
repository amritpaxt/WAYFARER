from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import CATEGORY_STAT, REVEAL_QUEST_THRESHOLD, REWARDS
from .database import Base, SessionLocal, engine, get_db
from .models import Episode, Quest, ShopItem, UnlockedFragment, User
from .schemas import CharacterOut, Credentials, QuestCreate, QuestOut, ShopItemOut, Token
from .security import create_token, current_user, hash_password, verify_password
from .seed import seed
from .services import apply_login_tick, character_payload, complete_quest, create_user_profile, completed_today_count


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db)
    yield


app = FastAPI(title="Wayfarer API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(credentials: Credentials, db: Session = Depends(get_db)):
    email = str(credentials.email).lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An arrival has already been recorded for this email")
    user = User(email=email, hashed_password=hash_password(credentials.password))
    db.add(user)
    db.flush()
    create_user_profile(db, user)
    db.commit()
    return Token(access_token=create_token(user.id))


@app.post("/auth/login", response_model=Token)
def login(credentials: Credentials, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(credentials.email).lower()))
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="The town does not recognize those credentials")
    return Token(access_token=create_token(user.id))


@app.get("/character/me", response_model=CharacterOut)
def get_character(user: User = Depends(current_user)):
    return character_payload(user.character)


@app.post("/character/login-tick")
def login_tick(user: User = Depends(current_user), db: Session = Depends(get_db)):
    missed_days = apply_login_tick(user.character)
    db.commit()
    return {"missed_days": missed_days, "character": character_payload(user.character)}


@app.get("/quests", response_model=list[QuestOut])
def list_quests(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Quest).where(Quest.user_id == user.id).order_by(Quest.is_completed, Quest.created_at.desc())).all()


@app.post("/quests", response_model=QuestOut, status_code=status.HTTP_201_CREATED)
def create_quest(payload: QuestCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if payload.category not in CATEGORY_STAT or payload.difficulty not in REWARDS:
        raise HTTPException(status_code=422, detail="Unknown quest category or difficulty")
    rewards = REWARDS[payload.difficulty]
    quest = Quest(user_id=user.id, title=payload.title.strip(), category=payload.category, difficulty=payload.difficulty, xp_reward=rewards["xp"], gold_reward=rewards["gold"], resource_reward=rewards["resource"])
    db.add(quest)
    db.commit()
    db.refresh(quest)
    return quest


@app.patch("/quests/{quest_id}/complete")
def mark_quest_complete(quest_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    quest = db.scalar(select(Quest).where(Quest.id == quest_id, Quest.user_id == user.id))
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    if quest.is_completed:
        raise HTTPException(status_code=409, detail="Quest is already complete")
    unlocked = complete_quest(db, user, quest)
    return {"quest": QuestOut.model_validate(quest), "newly_unlocked": [row.fragment_index for row in unlocked], "character": character_payload(user.character)}


@app.delete("/quests/{quest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quest(quest_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    quest = db.scalar(select(Quest).where(Quest.id == quest_id, Quest.user_id == user.id))
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    db.delete(quest)
    db.commit()


@app.get("/story/day/{day_number}")
def story_day(day_number: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    episode = db.scalar(select(Episode).where(Episode.day_number == day_number))
    if not episode:
        raise HTTPException(status_code=404, detail="Day not found")
    if day_number != 1:
        return {"day_number": day_number, "title": episode.title, "is_teaser": True, "fragments": [], "reveal": None}
    rows = db.scalars(select(UnlockedFragment).where(UnlockedFragment.user_id == user.id, UnlockedFragment.episode_id == episode.id).order_by(UnlockedFragment.fragment_index)).all()
    fragments, reveal = [], None
    for row in rows:
        source = episode.fragments_hard if row.variant_shown == "hard" else episode.fragments_normal
        if row.fragment_index < len(source):
            fragments.append({"index": row.fragment_index, "text": source[row.fragment_index], "variant": row.variant_shown, "unlocked_at": row.unlocked_at})
        else:
            reveal = {"text": episode.reveal_hard if row.variant_shown == "hard" else episode.reveal_normal, "variant": row.variant_shown, "unlocked_at": row.unlocked_at}
    completed = completed_today_count(db, user.id)
    return {"day_number": 1, "title": episode.title, "is_teaser": False, "setup": "You wake in the town with no memory. Local officers bring you in and tell you that you are their Chief, missing after a lead went wrong and found after hours of searching.", "fragments": fragments, "reveal": reveal, "progress": {"completed_today": completed, "fragment_count": len(fragments), "fragment_total": len(episode.fragments_normal), "reveal_threshold": REVEAL_QUEST_THRESHOLD}}


@app.get("/shop/items", response_model=list[ShopItemOut])
def shop_items(db: Session = Depends(get_db)):
    return db.scalars(select(ShopItem).order_by(ShopItem.cost)).all()
