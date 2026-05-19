# backend/app/db/models/game_move.py
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, JSONBType, UUIDType
from app.utils.constants import MoveType


class GameMove(Base):
    """Ordered move log used for replay and anti-cheat auditability."""

    __tablename__ = "game_moves"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    game_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("games.id", ondelete="CASCADE"), index=True, nullable=False)
    player_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    move_type: Mapped[MoveType] = mapped_column(
        Enum(MoveType, values_callable=lambda enum: [item.value for item in enum], native_enum=False),
        nullable=False,
    )
    payload: Mapped[dict] = mapped_column(JSONBType, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), index=True, nullable=False)

    game = relationship("Game", back_populates="moves")
