# backend/app/db/models/user.py
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDType
from app.utils.constants import OnlineStatus, UserRole


class User(TimestampMixin, Base):
    """Application profile synced from Supabase Auth."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(24), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(2048))
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    win_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lose_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    online_status: Mapped[OnlineStatus] = mapped_column(
        Enum(OnlineStatus, values_callable=lambda enum: [item.value for item in enum], native_enum=False),
        default=OnlineStatus.OFFLINE,
        nullable=False,
    )
    last_seen: Mapped[datetime | None] = mapped_column()
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=lambda enum: [item.value for item in enum], native_enum=False),
        default=UserRole.PLAYER,
        nullable=False,
    )

    hosted_rooms = relationship("Room", back_populates="host")
    room_memberships = relationship("RoomPlayer", back_populates="user", cascade="all, delete-orphan")
