from app.services import xp_required_for_next_level
from app.config import REVEAL_QUEST_THRESHOLD

def test_xp_curve_increases():
    assert xp_required_for_next_level(1) == 100
    assert xp_required_for_next_level(2) > xp_required_for_next_level(1)

def test_fragment_thresholds_are_ordered():
    assert REVEAL_QUEST_THRESHOLD >= 2 * 3
