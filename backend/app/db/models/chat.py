# backend/app/db/models/chat.py
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDType
from app.utils.constants import ChatType


class Chat(Base):
    """Room, team, and spectator chat messages."""

    __tablename__ = "chats"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    room_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("rooms.id", ondelete="CASCADE"), index=True, nullable=False)
    sender_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[ChatType] = mapped_column(
        Enum(ChatType, values_callable=lambda enum: [item.value for item in enum], native_enum=False),
        default=ChatType.ROOM,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), index=True, nullable=False)

    room = relationship("Room", back_populates="chats")
