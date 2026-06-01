# backend/app/api/dependencies/rate_limit.py
import logging
import time

from fastapi import Depends, Request
from redis.exceptions import RedisError

from app.api.dependencies.auth_deps import get_current_user
from app.core.config import get_settings
from app.core.redis import disconnect_redis_pool
from app.db.models.user import User
from app.utils.exceptions import RateLimitError

logger = logging.getLogger(__name__)


async def user_route_rate_limit(request: Request, user: User = Depends(get_current_user)) -> None:
    """Apply a Redis sliding-window limit per user and route."""
    redis = getattr(request.app.state, "redis", None)
    if redis is None or getattr(request.app.state, "redis_available", True) is False:
        return
    manager = getattr(request.app.state, "websocket_manager", None)
    settings = manager.settings if manager is not None else get_settings()
    now = int(time.time() * 1000)
    window_ms = settings.RATE_LIMIT_WINDOW_SECONDS * 1000
    key = f"ratelimit:{user.id}:{request.url.path}"
    try:
        await redis.zremrangebyscore(key, 0, now - window_ms)
        await redis.zadd(key, {str(now): now})
        count = await redis.zcard(key)
        await redis.pexpire(key, window_ms)
    except RedisError:
        request.app.state.redis_available = False
        logger.warning(
            "user_rate_limit_redis_unavailable",
            extra={"path": request.url.path, "user_id": str(user.id)},
            exc_info=True,
        )
        await disconnect_redis_pool(redis)
        return
    if count > settings.RATE_LIMIT_REQUESTS:
        raise RateLimitError()
