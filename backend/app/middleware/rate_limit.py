# backend/app/middleware/rate_limit.py
import logging
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import ORJSONResponse
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import Settings
from app.core.redis import disconnect_redis_pool
from app.utils.responses import error_response

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-backed app-level fixed-window rate limiting by IP."""

    def __init__(self, app: object, settings: Settings) -> None:
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.url.path in {"/health", "/metrics"}:
            return await call_next(request)
        redis = getattr(request.app.state, "redis", None)
        if redis is None or getattr(request.app.state, "redis_available", True) is False:
            return await call_next(request)
        client_ip = (
            request.headers.get("x-real-ip")
            or (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown")
        )
        key = f"ratelimit:ip:{client_ip}:{request.url.path}"
        try:
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, self.settings.RATE_LIMIT_WINDOW_SECONDS)
        except RedisError:
            request.app.state.redis_available = False
            logger.warning(
                "rate_limit_redis_unavailable",
                extra={"path": request.url.path, "client_ip": client_ip},
                exc_info=True,
            )
            await disconnect_redis_pool(redis)
            return await call_next(request)
        if count > self.settings.RATE_LIMIT_REQUESTS:
            return ORJSONResponse(content=error_response("rate_limited", "Too many requests"), status_code=429)
        return await call_next(request)
