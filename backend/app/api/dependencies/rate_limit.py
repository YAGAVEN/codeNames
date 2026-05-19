# backend/app/api/dependencies/rate_limit.py
import time

from fastapi import Depends, Request

from app.api.dependencies.auth_deps import get_current_user
from app.core.config import get_settings
from app.db.models.user import User
from app.utils.exceptions import RateLimitError


async def user_route_rate_limit(request: Request, user: User = Depends(get_current_user)) -> None:
    """Apply a Redis sliding-window limit per user and route."""
    redis = getattr(request.app.state, "redis", None)
    if redis is None:
        return
    manager = getattr(request.app.state, "websocket_manager", None)
    settings = manager.settings if manager is not None else get_settings()
    now = int(time.time() * 1000)
    window_ms = settings.RATE_LIMIT_WINDOW_SECONDS * 1000
    key = f"ratelimit:{user.id}:{request.url.path}"
    await redis.zremrangebyscore(key, 0, now - window_ms)
    await redis.zadd(key, {str(now): now})
    count = await redis.zcard(key)
    await redis.pexpire(key, window_ms)
    if count > settings.RATE_LIMIT_REQUESTS:
        raise RateLimitError()
