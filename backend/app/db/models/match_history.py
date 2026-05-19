# backend/app/db/models/match_history.py
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDType
from app.utils.constants import PlayerRole, Team


class MatchHistory(Base):
    """Per-player outcome and stat row for a completed game."""

    __tablename__ = "match_history"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    game_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("games.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    team: Mapped[Team] = mapped_column(
        Enum(Team, values_callable=lambda enum: [item.value for item in enum], native_enum=False),
        nullable=False,
    )
    role: Mapped[PlayerRole] = mapped_column(
        Enum(PlayerRole, values_callable=lambda enum: [item.value for item in enum], native_enum=False),
        nullable=False,
    )
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clues_given: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct_guesses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), index=True, nullable=False)

    game = relationship("Game", back_populates="history")
