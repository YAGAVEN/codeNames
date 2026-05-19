# backend/app/tests/unit/test_board_generator.py
from app.game.board_generator import generate_board
from app.game.word_service import DEFAULT_WORD_PACKS


def test_generate_board_is_reproducible() -> None:
    """Board generation should be deterministic for replay support."""
    words = DEFAULT_WORD_PACKS["cities"]
    first = generate_board(words, "seed-1")
    second = generate_board(words, "seed-1")
    assert first == second
    assert len(first) == 25
    counts = {team: sum(1 for card in first if card["team"] == team) for team in {"red", "blue", "neutral", "assassin"}}
    assert counts == {"red": 9, "blue": 8, "neutral": 7, "assassin": 1}
