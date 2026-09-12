from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_URL = f"sqlite:///{BASE_DIR / 'wayfarer.db'}"
JWT_SECRET = "change-this-before-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7
REVEAL_QUEST_THRESHOLD = 8
RESOURCE_DECAY_PER_MISSED_DAY = 5
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in {"1", "true", "yes", "on"}

REWARDS = {
    "Easy": {"xp": 10, "gold": 5, "resource": 5},
    "Medium": {"xp": 25, "gold": 12, "resource": 10},
    "Hard": {"xp": 50, "gold": 25, "resource": 15},
}
CATEGORY_STAT = {
    "Gym/Sports/Chores": "Strength",
    "Coding/Study": "Intellect",
    "Reading/Reflection": "Wisdom",
    "Sleep/Health/Self-care": "Vitality",
}
STAT_NAMES = tuple(CATEGORY_STAT.values())
