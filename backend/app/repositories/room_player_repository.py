# backend/app/repositories/room_player_repository.py
from uuid import UUID

from sqlalchemy import func, select

from app.db.models.room_player import RoomPlayer
from app.db.models.user import User
from app.repositories.base import BaseRepository
from app.utils.constants import PlayerRole, Team


class RoomPlayerRepository(BaseRepository[RoomPlayer]):
    """Database operations for room memberships."""

    model = RoomPlayer

    async def add_player(self, room_id: UUID, user_id: UUID, team: Team = Team.SPECTATOR) -> RoomPlayer:
        """Add a user to a room."""
        player = RoomPlayer(room_id=room_id, user_id=user_id, team=team, role=PlayerRole.OPERATIVE)
        return await self.add(player)

    async def get_membership(self, room_id: UUID, user_id: UUID) -> RoomPlayer | None:
        """Return a user's room membership."""
        result = await self.session.execute(
            select(RoomPlayer).where(RoomPlayer.room_id == room_id, RoomPlayer.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_by_room(self, room_id: UUID) -> list[tuple[RoomPlayer, User | None]]:
        """Return players with optional profile details."""
        result = await self.session.execute(
            select(RoomPlayer, User)
            .join(User, User.id == RoomPlayer.user_id, isouter=True)
            .where(RoomPlayer.room_id == room_id)
            .order_by(RoomPlayer.joined_at.asc())
        )
        return [(row[0], row[1]) for row in result.all()]

    async def count_by_room(self, room_id: UUID) -> int:
        """Count players in a room."""
        result = await self.session.execute(select(func.count()).select_from(RoomPlayer).where(RoomPlayer.room_id == room_id))
        return int(result.scalar_one())

    async def set_ready(self, room_id: UUID, user_id: UUID, is_ready: bool) -> RoomPlayer | None:
        """Mark a room member ready or unready."""
        membership = await self.get_membership(room_id, user_id)
        if membership is not None:
            membership.is_ready = is_ready
            await self.session.flush()
        return membership

    async def remove_player(self, room_id: UUID, user_id: UUID) -> None:
        """Remove a user from a room."""
        membership = await self.get_membership(room_id, user_id)
        if membership is not None:
            await self.delete(membership)
