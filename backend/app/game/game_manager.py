# backend/app/game/game_manager.py
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.game.board_generator import generate_board
from app.utils.constants import MoveType, PlayerRole, RoomStatus, Team
from app.utils.exceptions import GameRuleError

_game_states: dict[str, dict[str, Any]] = {}


class GameManager:
    """Server-authoritative game state machine backed by process memory."""

    async def start_game(self, room_id: UUID | str, words: list[str], seed: str | int, word_pack: str) -> dict[str, Any]:
        """Create an in-progress state and persist it in memory."""
        board = generate_board(words, seed)
        state = {
            "room_id": str(room_id),
            "status": RoomStatus.IN_PROGRESS.value,
            "seed": str(seed),
            "word_pack": word_pack,
            "board": board,
            "current_team": Team.RED.value,
            "current_clue": None,
            "scores": {Team.RED.value: 0, Team.BLUE.value: 0},
            "moves": [],
            "winner_team": None,
            "started_at": datetime.now(UTC).isoformat(),
            "ended_at": None,
        }
        await self.save_state(room_id, state)
        return state

    async def load_state(self, room_id: UUID | str) -> dict[str, Any]:
        """Load the latest game state snapshot from memory."""
        state = _game_states.get(str(room_id))
        if state is None:
            raise GameRuleError("Game state was not found")
        return dict(state)

    async def save_state(self, room_id: UUID | str, state: dict[str, Any]) -> None:
        """Persist a full game-state snapshot after every move."""
        _game_states[str(room_id)] = dict(state)

    async def give_clue(
        self,
        room_id: UUID | str,
        user_id: UUID | str,
        team: Team,
        role: PlayerRole,
        clue_word: str,
        clue_number: int,
    ) -> dict[str, Any]:
        """Validate and apply a spymaster clue."""
        state = await self.load_state(room_id)
        self.validate_clue(state, team, role, clue_word, clue_number)
        state["current_clue"] = {"word": clue_word.strip(), "number": clue_number, "remaining": clue_number + 1}
        state["moves"].append(
            {
                "type": MoveType.CLUE.value,
                "player_id": str(user_id),
                "team": team.value,
                "payload": state["current_clue"],
                "created_at": datetime.now(UTC).isoformat(),
            }
        )
        await self.save_state(room_id, state)
        return state

    async def select_card(
        self,
        room_id: UUID | str,
        user_id: UUID | str,
        team: Team,
        role: PlayerRole,
        card_index: int,
    ) -> dict[str, Any]:
        """Validate and apply an operative card selection."""
        state = await self.load_state(room_id)
        self.validate_guess(state, team, role, card_index)
        card = state["board"][card_index]
        card["revealed"] = True
        card["revealed_by"] = str(user_id)
        if card["team"] in (Team.RED.value, Team.BLUE.value):
            state["scores"][card["team"]] += 1

        winner = self.detect_winner(state, card["team"])
        if winner:
            state["status"] = RoomStatus.FINISHED.value
            state["winner_team"] = winner
            state["ended_at"] = datetime.now(UTC).isoformat()
        elif card["team"] != team.value:
            state = self.advance_turn(state)
        else:
            state["current_clue"]["remaining"] -= 1
            if state["current_clue"]["remaining"] <= 0:
                state = self.advance_turn(state)

        state["moves"].append(
            {
                "type": MoveType.GUESS.value,
                "player_id": str(user_id),
                "team": team.value,
                "payload": {"card_index": card_index, "card_team": card["team"]},
                "created_at": datetime.now(UTC).isoformat(),
            }
        )
        await self.save_state(room_id, state)
        return state

    async def end_turn(self, room_id: UUID | str, user_id: UUID | str, team: Team) -> dict[str, Any]:
        """End the current team's turn."""
        state = await self.load_state(room_id)
        if state["current_team"] != team.value:
            raise GameRuleError("Only the current team can end its turn")
        state = self.advance_turn(state)
        state["moves"].append(
            {
                "type": MoveType.PASS.value,
                "player_id": str(user_id),
                "team": team.value,
                "payload": {},
                "created_at": datetime.now(UTC).isoformat(),
            }
        )
        await self.save_state(room_id, state)
        return state

    def validate_clue(self, state: dict[str, Any], team: Team, role: PlayerRole, clue_word: str, clue_number: int) -> None:
        """Ensure a clue is legal and comes from the current team's spymaster."""
        if state["status"] != RoomStatus.IN_PROGRESS.value:
            raise GameRuleError("Game is not in progress")
        if state["current_team"] != team.value:
            raise GameRuleError("It is not this team's turn")
        if role != PlayerRole.SPYMASTER:
            raise GameRuleError("Only the spymaster can give a clue")
        if not 1 <= clue_number <= 9:
            raise GameRuleError("Clue number must be between 1 and 9")
        board_words = {str(card["word"]).casefold() for card in state["board"]}
        if clue_word.strip().casefold() in board_words:
            raise GameRuleError("Clue cannot be a word on the board")
        if state.get("current_clue"):
            raise GameRuleError("A clue is already active")

    def validate_guess(self, state: dict[str, Any], team: Team, role: PlayerRole, card_index: int) -> None:
        """Ensure a card selection is legal and comes from an operative."""
        if state["status"] != RoomStatus.IN_PROGRESS.value:
            raise GameRuleError("Game is not in progress")
        if state["current_team"] != team.value:
            raise GameRuleError("It is not this team's turn")
        if role != PlayerRole.OPERATIVE:
            raise GameRuleError("Only operatives can select cards")
        if not state.get("current_clue"):
            raise GameRuleError("A clue is required before guessing")
        if card_index < 0 or card_index >= len(state["board"]):
            raise GameRuleError("Card index is out of range")
        if state["board"][card_index]["revealed"]:
            raise GameRuleError("Card is already revealed")

    def detect_winner(self, state: dict[str, Any], revealed_team: str) -> str | None:
        """Detect assassin or all-team-card win conditions."""
        if revealed_team == "assassin":
            return Team.BLUE.value if state["current_team"] == Team.RED.value else Team.RED.value
        for team in (Team.RED.value, Team.BLUE.value):
            team_cards = [card for card in state["board"] if card["team"] == team]
            if all(card["revealed"] for card in team_cards):
                return team
        return None

    def advance_turn(self, state: dict[str, Any]) -> dict[str, Any]:
        """Switch teams and clear the active clue."""
        state["current_team"] = Team.BLUE.value if state["current_team"] == Team.RED.value else Team.RED.value
        state["current_clue"] = None
        return state
