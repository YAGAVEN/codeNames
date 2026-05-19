# backend/app/repositories/achievement_repository.py
from uuid import UUID

from sqlalchemy import select

from app.db.models.achievement import Achievement
from app.repositories.base import BaseRepository


class AchievementRepository(BaseRepository[Achievement]):
    """Database operations for achievements."""

    model = Achievement

    async def unlock(self, user_id: UUID, badge_key: str) -> Achievement:
        """Record an achievement unlock if a caller has already checked idempotency."""
        achievement = Achievement(user_id=user_id, badge_key=badge_key)
        return await self.add(achievement)

    async def list_for_user(self, user_id: UUID) -> list[Achievement]:
        """List achievements for a user."""
        result = await self.session.execute(select(Achievement).where(Achievement.user_id == user_id))
        return list(result.scalars().all())
