# backend/app/db/models/room_player.py
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDType
from app.utils.constants import PlayerRole, Team


class RoomPlayer(Base):
    """Membership of a player in a room."""

    __tablename__ = "room_players"
    __table_args__ = (UniqueConstraint("room_id", "user_id", name="uq_room_players_room_user"),)

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    room_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("rooms.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    team: Mapped[Team] = mapped_column(
        Enum(Team, values_callable=lambda enum: [item.value for item in enum], native_enum=False),
        default=Team.SPECTATOR,
        nullable=False,
    )
    role: Mapped[PlayerRole] = mapped_column(
        Enum(PlayerRole, values_callable=lambda enum: [item.value for item in enum], native_enum=False),
        default=PlayerRole.OPERATIVE,
        nullable=False,
    )
    is_ready: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    room = relationship("Room", back_populates="players")
    user = relationship("User", back_populates="room_memberships")
