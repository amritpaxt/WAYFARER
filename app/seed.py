from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Episode, ShopItem


DAY_ONE_NORMAL = [
    "Rain ticks against rusted metal outside the station. The smell reaches him before the sound does, and it lands in his chest like a memory with its name scraped away.",
    "At the corner of Bell and Ash, he stops without knowing why. The cracked curb, the dead traffic light, the narrow shopfront - all of it feels painfully familiar. They told him he had never lived here before the incident.",
    "An officer calls him \"Rook\" while passing a case file. The name is absent from every intake form. When he asks, the officer laughs too quickly and says it is nothing.",
]
DAY_ONE_HARD = [
    "The smell. Rain on rust. It reaches him first, before the sound, and something inside him answers. He has never been here. He has. Hasn't he?",
    "Bell and Ash. The corner waits for him. Cracked curb. Dead light. The place knows his feet better than he does, though they insist he never lived here before this.",
    "\"Rook.\" The officer says it like a reflex. Not on the forms. Not anywhere. The laugh comes too fast when he asks, and the word is suddenly nothing. Supposedly.",
]
REVEAL_NORMAL = "Alone in the office they insist is his, he opens the bottom drawer and finds a note in handwriting that must be his own: 'Don't trust the badge. Not even yours.' The words contradict every careful answer the town has given him."
REVEAL_HARD = "His office. Their words, not his. Bottom drawer. A note in his hand - or did he find it there? The handwriting is his, he thinks. It says: 'Don't trust the badge. Not even yours.' The station hums around him as if it already knew."


def seed(db: Session) -> None:
    if not db.scalar(select(Episode).where(Episode.day_number == 1)):
        db.add(Episode(day_number=1, title="The Man With No Name", fragments_normal=DAY_ONE_NORMAL, fragments_hard=DAY_ONE_HARD, reveal_normal=REVEAL_NORMAL, reveal_hard=REVEAL_HARD, unlock_resource_threshold=35))
    for day in range(2, 8):
        if not db.scalar(select(Episode).where(Episode.day_number == day)):
            db.add(Episode(day_number=day, title=f"Day {day}: Classified", fragments_normal=[], fragments_hard=[], reveal_normal=None, reveal_hard=None, unlock_resource_threshold=35))
    if not db.scalar(select(ShopItem).where(ShopItem.name == "Rusted Service Pin")):
        db.add(ShopItem(name="Rusted Service Pin", cost=40, description="A cosmetic relic from a department with no records."))
    db.commit()
