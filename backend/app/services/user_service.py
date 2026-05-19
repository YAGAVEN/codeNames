# backend/app/services/user_service.py
import asyncio
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_supabase_admin_client
from app.repositories.user_repository import UserRepository
from app.schemas.users import LeaderboardEntry, UserUpdate
from app.utils.exceptions import NotFoundError


class UserService:
    """User profile, avatar, and leaderboard logic."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.users = UserRepository(session)
        self.settings = settings

    async def get_user(self, user_id: UUID) -> object:
        """Return a user profile by id."""
        user = await self.users.get(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user

    async def update_me(self, user_id: UUID, payload: UserUpdate) -> object:
        """Update the current user's profile."""
        user = await self.users.get(user_id)
        if user is None:
            raise NotFoundError("User not found")
        updated = await self.users.update_profile(user, payload)
        await self.users.commit()
        return await self.users.refresh(updated)

    async def upload_avatar(self, user_id: UUID, file: UploadFile) -> str:
        """Upload avatar bytes to Supabase Storage and update the profile."""
        user = await self.users.get(user_id)
        if user is None:
            raise NotFoundError("User not found")
        content = await file.read()
        path = f"{user_id}/{file.filename}"
        client = get_supabase_admin_client()
        if client is not None:
            await asyncio.to_thread(
                client.storage.from_(self.settings.AVATARS_BUCKET).upload,
                path,
                content,
                {"content-type": file.content_type or "application/octet-stream", "upsert": "true"},
            )
            public = client.storage.from_(self.settings.AVATARS_BUCKET).get_public_url(path)
            avatar_url = public if isinstance(public, str) else str(public)
        else:
            # TODO: Configure Supabase Storage; development returns deterministic placeholder URL.
            avatar_url = f"/static/dev-avatars/{path}"
        updated = await self.users.update_profile(user, UserUpdate(avatar_url=avatar_url))
        await self.users.commit()
        await self.users.refresh(updated)
        return avatar_url

    async def leaderboard(self, limit: int = 50) -> list[LeaderboardEntry]:
        """Return ranked leaderboard entries."""
        users = await self.users.leaderboard(limit)
        return [
            LeaderboardEntry(
                id=user.id,
                username=user.username,
                avatar_url=user.avatar_url,
                xp=user.xp,
                level=user.level,
                win_count=user.win_count,
                rank=index + 1,
            )
            for index, user in enumerate(users)
        ]
