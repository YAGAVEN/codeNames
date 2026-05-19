# backend/app/repositories/notification_repository.py
from uuid import UUID

from sqlalchemy import select

from app.db.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Database operations for notifications."""

    model = Notification

    async def create(self, user_id: UUID, notification_type: str, payload: dict) -> Notification:
        """Create an unread notification."""
        notification = Notification(user_id=user_id, type=notification_type, payload=payload)
        return await self.add(notification)

    async def list_unread(self, user_id: UUID) -> list[Notification]:
        """List unread notifications."""
        result = await self.session.execute(
            select(Notification).where(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        return list(result.scalars().all())
