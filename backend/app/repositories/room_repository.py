# backend/app/repositories/room_repository.py
from uuid import UUID

from sqlalchemy import func, select

from app.db.models.room import Room
from app.db.models.room_player import RoomPlayer
from app.repositories.base import BaseRepository
from app.utils.constants import RoomStatus


class RoomRepository(BaseRepository[Room]):
    """Database operations for rooms."""

    model = Room

    async def create(self, room_code: str, host_id: UUID, max_players: int, settings: dict) -> Room:
        """Create a new waiting room."""
        room = Room(room_code=room_code, host_id=host_id, max_players=max_players, settings=settings, game_state={})
        return await self.add(room)

    async def get_by_code(self, room_code: str) -> Room | None:
        """Fetch a room by public code."""
        result = await self.session.execute(select(Room).where(Room.room_code == room_code))
        return result.scalar_one_or_none()

    async def list_public(self, limit: int, offset: int) -> list[tuple[Room, int]]:
        """Return public rooms with player counts."""
        result = await self.session.execute(
            select(Room, func.count(RoomPlayer.id))
            .outerjoin(RoomPlayer, RoomPlayer.room_id == Room.id)
            .where(Room.status == RoomStatus.WAITING)
            .group_by(Room.id)
            .order_by(Room.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [(row[0], int(row[1])) for row in result.all()]

    async def count(self, status: RoomStatus | None = None) -> int:
        """Count rooms, optionally by status."""
        statement = select(func.count()).select_from(Room)
        if status is not None:
            statement = statement.where(Room.status == status)
        result = await self.session.execute(statement)
        return int(result.scalar_one())
