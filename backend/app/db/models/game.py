# backend/app/db/models/game.py
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, JSONBType, UUIDType
from app.utils.constants import Team


class Game(Base):
    """Completed or in-progress match attached to a room."""

    __tablename__ = "games"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    room_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("rooms.id", ondelete="CASCADE"), index=True, nullable=False)
    winner_team: Mapped[Team | None] = mapped_column(
        Enum(Team, values_callable=lambda enum: [item.value for item in enum], native_enum=False)
    )
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    red_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blue_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    replay_data: Mapped[dict] = mapped_column(JSONBType, default=dict, nullable=False)
    word_pack: Mapped[str] = mapped_column(String(64), default="default", nullable=False)
    started_at: Mapped[datetime | None] = mapped_column()
    ended_at: Mapped[datetime | None] = mapped_column()

    room = relationship("Room", back_populates="games")
    moves = relationship("GameMove", back_populates="game", cascade="all, delete-orphan")
    history = relationship("MatchHistory", back_populates="game", cascade="all, delete-orphan")
