# backend/app/api/dependencies/auth_deps.py
from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db_deps import get_db
from app.core.security import decode_token, extract_bearer_token
from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.constants import OnlineStatus, UserRole
from app.utils.exceptions import AuthenticationError, AuthorizationError


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Authenticate the bearer JWT and load the current user."""
    token = extract_bearer_token(authorization)
    payload = decode_token(token)
    user = await UserRepository(db).get(UUID(str(payload["sub"])))
    if user is None:
        raise AuthenticationError("User not found")
    if user.online_status == OnlineStatus.BANNED:
        raise AuthorizationError("Account is banned")
    return user


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    """Create a dependency that enforces role-based access."""

    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise AuthorizationError("Insufficient role")
        return user

    return dependency


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin role for /admin routes."""
    if user.role != UserRole.ADMIN:
        raise AuthorizationError("Admin role required")
    return user


async def require_moderator(user: User = Depends(get_current_user)) -> User:
    """Require moderator or admin role."""
    if user.role not in {UserRole.MODERATOR, UserRole.ADMIN}:
        raise AuthorizationError("Moderator role required")
    return user
