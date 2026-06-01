# backend/app/tests/unit/test_game_manager.py
import pytest

from app.game.game_manager import GameManager
from app.game.word_service import DEFAULT_WORD_PACKS
from app.utils.constants import PlayerRole, Team
from app.utils.exceptions import GameRuleError


@pytest.mark.asyncio
async def test_game_manager_validates_clues_and_guesses() -> None:
    """A legal clue followed by a legal guess should update in-memory state."""
    manager = GameManager()
    state = await manager.start_game("room-1", DEFAULT_WORD_PACKS["cities"], "seed-2", "cities")
    board_word = state["board"][0]["word"]

    with pytest.raises(GameRuleError):
        await manager.give_clue("room-1", "u1", Team.RED, PlayerRole.SPYMASTER, board_word, 1)

    state = await manager.give_clue("room-1", "u1", Team.RED, PlayerRole.SPYMASTER, "travel", 2)
    red_index = next(card["index"] for card in state["board"] if card["team"] == "red")
    updated = await manager.select_card("room-1", "u2", Team.RED, PlayerRole.OPERATIVE, red_index)
    assert updated["board"][red_index]["revealed"] is True
    assert updated["scores"]["red"] == 1
