# backend/app/api/routes/users.py
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth_deps import get_current_user
from app.api.dependencies.db_deps import get_db
from app.api.dependencies.rate_limit import user_route_rate_limit
from app.core.config import get_settings
from app.db.models.user import User
from app.schemas.common import EnvelopeSchema
from app.schemas.users import AvatarUploadResponse, LeaderboardEntry, UserRead, UserUpdate
from app.services.user_service import UserService
from app.utils.responses import success_response

router = APIRouter()
settings = get_settings()


@router.get("/me", response_model=EnvelopeSchema[UserRead], summary="Current user")
async def me(_rate_limit: None = Depends(user_route_rate_limit), user: User = Depends(get_current_user)) -> dict:
    """Return current user profile."""
    return success_response(user)


@router.put("/me", response_model=EnvelopeSchema[UserRead], summary="Update current user")
async def update_me(
    payload: UserUpdate,
    _rate_limit: None = Depends(user_route_rate_limit),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Update current user profile."""
    updated = await UserService(db, settings).update_me(user.id, payload)
    return success_response(updated)


@router.post("/me/avatar", response_model=EnvelopeSchema[AvatarUploadResponse], summary="Upload avatar")
async def upload_avatar(
    file: UploadFile,
    _rate_limit: None = Depends(user_route_rate_limit),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Upload avatar to Supabase Storage."""
    avatar_url = await UserService(db, settings).upload_avatar(user.id, file)
    return success_response(AvatarUploadResponse(avatar_url=avatar_url))


@router.get("/leaderboard", response_model=EnvelopeSchema[list[LeaderboardEntry]], summary="Leaderboard")
async def leaderboard(limit: int = 50, db: AsyncSession = Depends(get_db)) -> dict:
    """Return top players."""
    return success_response(await UserService(db, settings).leaderboard(limit))


@router.get("/{user_id}", response_model=EnvelopeSchema[UserRead], summary="Get user")
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    """Return public user profile."""
    user = await UserService(db, settings).get_user(user_id)
    return success_response(user)
