# backend/app/schemas/rooms.py
from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import StrictSchema
from app.utils.constants import PlayerRole, RoomStatus, Team


class RoomCreateRequest(StrictSchema):
    """Create a new game room."""

    max_players: int = Field(default=10, ge=4, le=12)
    settings: dict = Field(default_factory=dict)


class RoomJoinRequest(StrictSchema):
    """Join a room by public room code."""

    room_code: str = Field(min_length=4, max_length=8, examples=["DELHI7"])
    password: str | None = Field(default=None, max_length=64)
    team: Team = Team.SPECTATOR


class KickPlayerRequest(StrictSchema):
    """Kick a player from a hosted room."""

    user_id: UUID


class RoomPlayerRead(StrictSchema):
    """Room membership response."""

    user_id: UUID
    username: str | None = None
    team: Team
    role: PlayerRole
    is_ready: bool
    joined_at: datetime


class RoomRead(StrictSchema):
    """Room detail response."""

    id: UUID
    room_code: str
    host_id: UUID
    status: RoomStatus
    max_players: int
    settings: dict
    game_state: dict
    created_at: datetime
    updated_at: datetime
    players: list[RoomPlayerRead] = Field(default_factory=list)


class PublicRoomRead(StrictSchema):
    """Public room listing response."""

    id: UUID
    room_code: str
    host_id: UUID
    status: RoomStatus
    max_players: int
    player_count: int
    created_at: datetime
