# backend/app/db/models/tournament.py
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, JSONBType, UUIDType
from app.utils.constants import TournamentStatus


class Tournament(Base):
    """Scheduled tournament configuration."""

    __tablename__ = "tournaments"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    status: Mapped[TournamentStatus] = mapped_column(
        Enum(TournamentStatus, values_callable=lambda enum: [item.value for item in enum], native_enum=False),
        default=TournamentStatus.DRAFT,
        index=True,
        nullable=False,
    )
    settings: Mapped[dict] = mapped_column(JSONBType, default=dict, nullable=False)
    starts_at: Mapped[datetime | None] = mapped_column()
    ends_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
