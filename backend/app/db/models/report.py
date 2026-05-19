# backend/app/db/models/report.py
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDType
from app.utils.constants import ReportStatus


class Report(Base):
    """Moderation report created by a player."""

    __tablename__ = "reports"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    reporter_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    reported_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, values_callable=lambda enum: [item.value for item in enum], native_enum=False),
        default=ReportStatus.OPEN,
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), index=True, nullable=False)
