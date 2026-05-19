# backend/app/db/models/room.py
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, JSONBType, TimestampMixin, UUIDType
from app.utils.constants import RoomStatus


class Room(TimestampMixin, Base):
    """Game lobby and mutable game-state container."""

    __tablename__ = "rooms"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    room_code: Mapped[str] = mapped_column(String(8), unique=True, index=True, nullable=False)
    host_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[RoomStatus] = mapped_column(
        Enum(RoomStatus, values_callable=lambda enum: [item.value for item in enum], native_enum=False),
        default=RoomStatus.WAITING,
        index=True,
        nullable=False,
    )
    max_players: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    settings: Mapped[dict] = mapped_column(JSONBType, default=dict, nullable=False)
    game_state: Mapped[dict] = mapped_column(JSONBType, default=dict, nullable=False)

    host = relationship("User", back_populates="hosted_rooms")
    players = relationship("RoomPlayer", back_populates="room", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="room", cascade="all, delete-orphan")
    games = relationship("Game", back_populates="room", cascade="all, delete-orphan")
