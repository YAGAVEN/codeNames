# backend/app/services/friend_service.py
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.friendship_repository import FriendshipRepository
from app.repositories.user_repository import UserRepository
from app.utils.constants import FriendshipStatus
from app.utils.exceptions import AuthorizationError, ConflictError, NotFoundError

logger = logging.getLogger(__name__)


class FriendService:
    """Friend request and block-list business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self.friendships = FriendshipRepository(session)
        self.users = UserRepository(session)

    async def request(self, requester_id: UUID, addressee_id: UUID) -> object:
        """Create a friend request."""
        if requester_id == addressee_id:
            raise ConflictError("Cannot friend yourself")
        addressee = await self.users.get(addressee_id)
        if addressee is None:
            raise NotFoundError("User not found")
        friendship = await self.friendships.create(requester_id, addressee_id)
        await self.friendships.commit()
        await self.friendships.refresh(friendship)
        logger.info(
            "friend_request_email_requested",
            extra={"requester_id": str(requester_id), "addressee_id": str(addressee_id)},
        )
        return friendship

    async def accept(self, user_id: UUID, friendship_id: UUID) -> object:
        """Accept an incoming request."""
        friendship = await self.friendships.get(friendship_id)
        if friendship is None:
            raise NotFoundError("Friend request not found")
        if friendship.addressee_id != user_id:
            raise AuthorizationError("Only the addressee can accept this request")
        updated = await self.friendships.set_status(friendship, FriendshipStatus.ACCEPTED)
        await self.friendships.commit()
        return updated

    async def remove(self, user_id: UUID, friendship_id: UUID) -> None:
        """Remove a friendship involving the current user."""
        friendship = await self.friendships.get(friendship_id)
        if friendship is None:
            raise NotFoundError("Friendship not found")
        if user_id not in {friendship.requester_id, friendship.addressee_id}:
            raise AuthorizationError("Cannot remove this friendship")
        await self.friendships.delete(friendship)
        await self.friendships.commit()

    async def block(self, user_id: UUID, friendship_id: UUID) -> object:
        """Block a friendship or request."""
        friendship = await self.friendships.get(friendship_id)
        if friendship is None:
            raise NotFoundError("Friendship not found")
        if user_id not in {friendship.requester_id, friendship.addressee_id}:
            raise AuthorizationError("Cannot block this friendship")
        updated = await self.friendships.set_status(friendship, FriendshipStatus.BLOCKED)
        await self.friendships.commit()
        return updated

    async def list(self, user_id: UUID) -> list[object]:
        """List accepted friends."""
        return await self.friendships.list_for_user(user_id, FriendshipStatus.ACCEPTED)

    async def requests(self, user_id: UUID) -> list[object]:
        """List incoming pending requests."""
        return await self.friendships.list_requests(user_id)
