# backend/app/middleware/rate_limit.py
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import Settings
from app.utils.responses import error_response

_ip_windows: dict[str, list[float]] = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory app-level sliding-window rate limiting by IP."""

    def __init__(self, app: object, settings: Settings) -> None:
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.url.path in {"/health", "/metrics"}:
            return await call_next(request)
        client_ip = (
            request.headers.get("x-real-ip")
            or (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown")
        )
        key = f"ratelimit:ip:{client_ip}:{request.url.path}"
        now = time.time()
        window_start = now - self.settings.RATE_LIMIT_WINDOW_SECONDS
        window = [timestamp for timestamp in _ip_windows.get(key, []) if timestamp >= window_start]
        window.append(now)
        _ip_windows[key] = window
        if len(window) > self.settings.RATE_LIMIT_REQUESTS:
            return ORJSONResponse(content=error_response("rate_limited", "Too many requests"), status_code=429)
        return await call_next(request)
