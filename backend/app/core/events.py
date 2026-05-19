# backend/app/core/events.py
import logging
from typing import Any

from fastapi import FastAPI
from redis.asyncio import Redis

from app.core.config import get_settings
from app.websocket.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


async def startup(app: FastAPI) -> None:
    """Initialise Redis-backed realtime infrastructure."""
    settings = get_settings()
    redis = Redis.from_url(settings.REDIS_URL, decode_responses=False)
    app.state.redis = redis
    app.state.websocket_manager = ConnectionManager(redis=redis, settings=settings)
    await app.state.websocket_manager.start()
    logger.info("runtime_started", extra={"env": settings.APP_ENV})


async def shutdown(app: FastAPI) -> None:
    """Close background listeners and network clients cleanly."""
    manager: ConnectionManager | None = getattr(app.state, "websocket_manager", None)
    if manager is not None:
        await manager.stop()
    redis: Redis | None = getattr(app.state, "redis", None)
    if redis is not None:
        await redis.aclose()
    logger.info("runtime_stopped")


def get_app_state(app: FastAPI) -> dict[str, Any]:
    """Return a small serialisable runtime snapshot for diagnostics."""
    return {
        "has_redis": hasattr(app.state, "redis"),
        "has_websocket_manager": hasattr(app.state, "websocket_manager"),
    }
