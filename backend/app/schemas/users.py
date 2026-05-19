# backend/app/schemas/users.py
from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.common import StrictSchema
from app.utils.constants import OnlineStatus, UserRole


class UserRead(StrictSchema):
    """Public user profile."""

    id: UUID
    username: str
    email: EmailStr
    avatar_url: str | None = None
    xp: int
    level: int
    win_count: int
    lose_count: int
    streak: int
    online_status: OnlineStatus
    last_seen: datetime | None = None
    role: UserRole
    created_at: datetime
    updated_at: datetime


class UserUpdate(StrictSchema):
    """Editable user profile fields."""

    username: str | None = Field(default=None, min_length=3, max_length=24)
    avatar_url: str | None = Field(default=None, max_length=2048)


class AvatarUploadResponse(StrictSchema):
    """Public avatar URL returned after Supabase Storage upload."""

    avatar_url: str


class LeaderboardEntry(StrictSchema):
    """Leaderboard row sorted by XP and wins."""

    id: UUID
    username: str
    avatar_url: str | None = None
    xp: int
    level: int
    win_count: int
    rank: int
