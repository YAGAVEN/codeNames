# backend/app/db/models/notification.py
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, JSONBType, UUIDType


class Notification(Base):
    """User notification with flexible payload data."""

    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONBType, default=dict, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
