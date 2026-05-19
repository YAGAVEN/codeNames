# backend/app/repositories/friendship_repository.py
from uuid import UUID

from sqlalchemy import or_, select

from app.db.models.friendship import Friendship
from app.repositories.base import BaseRepository
from app.utils.constants import FriendshipStatus


class FriendshipRepository(BaseRepository[Friendship]):
    """Database operations for friendships."""

    model = Friendship

    async def create(self, requester_id: UUID, addressee_id: UUID) -> Friendship:
        """Create a pending friend request."""
        friendship = Friendship(requester_id=requester_id, addressee_id=addressee_id)
        return await self.add(friendship)

    async def list_for_user(self, user_id: UUID, status: FriendshipStatus | None = None) -> list[Friendship]:
        """List friend relationships for a user."""
        statement = select(Friendship).where(or_(Friendship.requester_id == user_id, Friendship.addressee_id == user_id))
        if status is not None:
            statement = statement.where(Friendship.status == status)
        result = await self.session.execute(statement.order_by(Friendship.created_at.desc()))
        return list(result.scalars().all())

    async def list_requests(self, user_id: UUID) -> list[Friendship]:
        """List incoming pending requests."""
        result = await self.session.execute(
            select(Friendship).where(
                Friendship.addressee_id == user_id,
                Friendship.status == FriendshipStatus.PENDING,
            )
        )
        return list(result.scalars().all())

    async def set_status(self, friendship: Friendship, status: FriendshipStatus) -> Friendship:
        """Update friendship status."""
        friendship.status = status
        await self.session.flush()
        return friendship
