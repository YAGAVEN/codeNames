# backend/app/db/models/friendship.py
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDType
from app.utils.constants import FriendshipStatus


class Friendship(TimestampMixin, Base):
    """Directional friendship request between two users."""

    __tablename__ = "friendships"
    __table_args__ = (UniqueConstraint("requester_id", "addressee_id", name="uq_friendships_requester_addressee"),)

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    requester_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    addressee_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[FriendshipStatus] = mapped_column(
        Enum(FriendshipStatus, values_callable=lambda enum: [item.value for item in enum], native_enum=False),
        default=FriendshipStatus.PENDING,
        index=True,
        nullable=False,
    )
