from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Episode, ShopItem

# Hard variants preserve plot facts, but make Rook's perception fractured and unreliable.
STORY = [
    ("The Man With No Name", "You wake in a rain-soaked town with no memory. The officers call you their missing Chief.", ["Rain ticks against rusted metal outside the station. The smell reaches him before the sound, and it lands in his chest like a memory with its name scraped away.", "At Bell and Ash, the cracked curb and dead traffic light feel painfully familiar. They told him he had never lived here before the incident.", "An officer calls him Rook while passing a case file. The name is absent from every intake form; his laugh is too quick when asked."], "In his office's bottom drawer is a note in his own hand: 'Don't trust the badge. Not even yours.'"),
    ("The Quiet Witness", "A vanished bartender is the only name left on your first open case.", ["The Nightjar's stools are upside down, but one glass is still wet.", "Mara Vale's ledger has every patron crossed out except a circle split by a river.", "The coroner says Mara left town. Her coat is hanging behind the bar, warm from the radiator."], "A tape in the jukebox carries Mara's whisper: 'They did not erase you. You asked them to.'"),
    ("The River Circle", "The symbol draws you beneath the floodwall, where the town keeps its oldest records.", ["Beneath the floodwall, chalk circles bloom on concrete like pale eyes.", "A maintenance map marks seven houses connected to the station by old telephone lines.", "In a sealed locker, you find a photograph: yourself beside the cult's founder, both wearing badges."], "The photograph's date is three years before your reported appointment as Chief."),
    ("The Archivist's Lie", "The town archivist offers answers, then asks what you remember of the fire.", ["The archive smells of wet paper and extinguished candles.", "Archivist Ilyan shows you a newspaper naming you investigator on the Bell Street fire.", "The article's final paragraph has been carefully cut away, but ash still clings to the page."], "Ilyan admits the fire killed twelve people. The official report says you ordered the doors locked."),
    ("The House That Remembers", "A condemned house preserves a night no one agrees happened.", ["The house on Bell Street has no address, only the river-circle painted over its door.", "Inside, a child's room is arranged around a radio repeating police dispatches from the fire.", "A hidden wall holds your old recorder: 'If I come back empty, do not let me lead them again.'"], "The recorder ends with a second voice: 'We will make you useful anyway.'"),
    ("The Choir Below", "The cult gathers under the station while a storm cuts the town from the road.", ["A service tunnel beneath the station is lined with the missing townspeople's shoes.", "The choir calls you Chief, then Witness, then Keeper.", "Mara steps from the crowd alive, carrying the badge you lost three years ago."], "Mara says you infiltrated the cult, then chose to erase your own memory when the ritual began to work."),
    ("Final Vow", "Before dawn, you decide what kind of Chief can survive the truth.", ["The storm breaks over the station and every telephone in town rings once.", "Your case files reveal the ritual was built from your investigation: a way to make witnesses carry one another's pain.", "At the river, the cult waits for your verdict—and the town waits to learn whether its Chief is still theirs."], "Your final vow is yours to make: protect the town, expose it, heal it, or endure it honestly."),
]


def fractured(text: str) -> str:
    return text.replace(". ", ". ").replace("You ", "You? ") + " The town insists this is the whole truth."


def seed(db: Session) -> None:
    for day, (title, setup, normal, reveal) in enumerate(STORY, 1):
        episode = db.scalar(select(Episode).where(Episode.day_number == day))
        hard = [fractured(text) for text in normal]
        if not episode:
            db.add(Episode(day_number=day, title=title, setup=setup, fragments_normal=normal, fragments_hard=hard, reveal_normal=reveal, reveal_hard=fractured(reveal), unlock_resource_threshold=35))
        else:
            episode.title, episode.setup = title, setup
            episode.fragments_normal, episode.fragments_hard = normal, hard
            episode.reveal_normal, episode.reveal_hard = reveal, fractured(reveal)
    for name, cost, description in [("Rusted Service Pin", 40, "A cosmetic relic from a department with no records."), ("Raincoat of the Missing", 75, "Keeps the weather off, not the memories."), ("River-Circle Signet", 120, "A seal worn by people who know too much."), ("Brass Desk Lamp", 160, "A warm light for a cold office.")]:
        if not db.scalar(select(ShopItem).where(ShopItem.name == name)):
            db.add(ShopItem(name=name, cost=cost, description=description))
    db.commit()
