# backend/app/db/models/achievement.py
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDType


class Achievement(Base):
    """Unlocked badge for a user."""

    __tablename__ = "achievements"
    __table_args__ = (UniqueConstraint("user_id", "badge_key", name="uq_achievements_user_badge"),)

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    badge_key: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
