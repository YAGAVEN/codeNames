# backend/app/schemas/matches.py
from datetime import datetime
from uuid import UUID

from app.schemas.common import StrictSchema
from app.utils.constants import MoveType, PlayerRole, Team


class GameMoveRead(StrictSchema):
    """Replay move item."""

    id: UUID
    game_id: UUID
    player_id: UUID
    move_type: MoveType
    payload: dict
    created_at: datetime


class MatchHistoryRead(StrictSchema):
    """Per-user match history response."""

    id: UUID
    game_id: UUID
    user_id: UUID
    team: Team
    role: PlayerRole
    is_winner: bool
    xp_earned: int
    clues_given: int
    correct_guesses: int
    created_at: datetime


class MatchRead(StrictSchema):
    """Game summary response."""

    id: UUID
    room_id: UUID
    winner_team: Team | None = None
    duration_seconds: int | None = None
    red_score: int
    blue_score: int
    replay_data: dict
    word_pack: str
    started_at: datetime | None = None
    ended_at: datetime | None = None


class ReplayRead(StrictSchema):
    """Structured replay export."""

    board: list[dict]
    moves: list[GameMoveRead]
    chat: list[dict]
