# backend/app/game/board_generator.py
import random
from collections.abc import Sequence
from typing import Any

from app.utils.constants import CARD_COUNTS, Team
from app.utils.exceptions import GameRuleError


def generate_board(word_pack: Sequence[str], seed: str | int) -> list[dict[str, Any]]:
    """Generate a reproducible 25-word Codenames board from a word pack."""
    unique_words = list(dict.fromkeys(word.strip() for word in word_pack if word.strip()))
    if len(unique_words) < 25:
        raise GameRuleError("Word pack must contain at least 25 unique words")

    rng = random.Random(str(seed))
    words = rng.sample(unique_words, 25)
    roles = (
        [Team.RED.value] * CARD_COUNTS[Team.RED]
        + [Team.BLUE.value] * CARD_COUNTS[Team.BLUE]
        + ["neutral"] * CARD_COUNTS["neutral"]
        + ["assassin"] * CARD_COUNTS["assassin"]
    )
    rng.shuffle(roles)

    return [
        {
            "index": index,
            "row": index // 5,
            "col": index % 5,
            "word": word,
            "team": roles[index],
            "revealed": False,
            "revealed_by": None,
        }
        for index, word in enumerate(words)
    ]
