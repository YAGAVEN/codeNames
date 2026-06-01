# backend/app/api/dependencies/rate_limit.py
import time

from fastapi import Depends, Request

from app.api.dependencies.auth_deps import get_current_user
from app.core.config import get_settings
from app.db.models.user import User
from app.utils.exceptions import RateLimitError

_rate_windows: dict[str, list[float]] = {}


async def user_route_rate_limit(request: Request, user: User = Depends(get_current_user)) -> None:
    """Apply an in-memory sliding-window limit per user and route."""
    manager = getattr(request.app.state, "websocket_manager", None)
    settings = manager.settings if manager is not None else get_settings()
    if not settings.RATE_LIMIT_ENABLED:
        return
    now = time.time()
    window_start = now - settings.RATE_LIMIT_WINDOW_SECONDS
    key = f"ratelimit:{user.id}:{request.url.path}"
    window = [timestamp for timestamp in _rate_windows.get(key, []) if timestamp >= window_start]
    window.append(now)
    _rate_windows[key] = window
    if len(window) > settings.RATE_LIMIT_REQUESTS:
        raise RateLimitError()
