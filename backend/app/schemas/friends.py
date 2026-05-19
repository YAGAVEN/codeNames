# backend/app/schemas/friends.py
from datetime import datetime
from uuid import UUID

from app.schemas.common import StrictSchema
from app.utils.constants import FriendshipStatus


class FriendRequestCreate(StrictSchema):
    """Create a friend request."""

    addressee_id: UUID


class FriendshipRead(StrictSchema):
    """Friendship or friend-request row."""

    id: UUID
    requester_id: UUID
    addressee_id: UUID
    status: FriendshipStatus
    created_at: datetime
    updated_at: datetime
