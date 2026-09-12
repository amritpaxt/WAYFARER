from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR / "wayfarer.db"))


def database_url(value: str | None) -> str:
    """Use SQLite locally and normalize ordinary Postgres URLs for psycopg."""
    if not value:
        return f"sqlite:///{DATABASE_PATH}"
    if value.startswith("postgres://"):
        value = f"postgresql://{value.removeprefix('postgres://')}"
    if value.startswith("postgresql://"):
        return f"postgresql+psycopg://{value.removeprefix('postgresql://')}"
    return value


DATABASE_URL = database_url(os.getenv("DATABASE_URL"))
# There is intentionally no fallback secret. The API refuses to start until a
# real secret is supplied, preventing accidentally forgeable production tokens.
JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7
REVEAL_QUEST_THRESHOLD = 8
RESOURCE_DECAY_PER_MISSED_DAY = 5
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in {"1", "true", "yes", "on"}
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()]

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
