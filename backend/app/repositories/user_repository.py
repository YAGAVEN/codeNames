# backend/app/repositories/user_repository.py
from uuid import UUID

from sqlalchemy import Select, func, select

from app.db.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.users import UserUpdate
from app.utils.constants import OnlineStatus


class UserRepository(BaseRepository[User]):
    """Database operations for users."""

    model = User

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by email."""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Fetch a user by username."""
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, username: str, email: str, user_id: UUID | None = None) -> User:
        """Create a local profile synced to Supabase auth."""
        user = User(id=user_id, username=username, email=email) if user_id else User(username=username, email=email)
        return await self.add(user)

    async def update_profile(self, user: User, payload: UserUpdate) -> User:
        """Update editable profile fields."""
        data = payload.model_dump(exclude_none=True)
        for key, value in data.items():
            setattr(user, key, value)
        await self.session.flush()
        return user

    async def set_online_status(self, user_id: UUID, status: OnlineStatus) -> None:
        """Update a user's online status."""
        user = await self.get(user_id)
        if user is not None:
            user.online_status = status
            await self.session.flush()

    async def leaderboard(self, limit: int = 50) -> list[User]:
        """Return top players by XP and wins."""
        result = await self.session.execute(
            select(User).order_by(User.xp.desc(), User.win_count.desc(), User.created_at.asc()).limit(limit)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        """Count all users."""
        result = await self.session.execute(select(func.count()).select_from(User))
        return int(result.scalar_one())

    def search_query(self) -> Select[tuple[User]]:
        """Return base user query for admin listing."""
        return select(User).order_by(User.created_at.desc())
