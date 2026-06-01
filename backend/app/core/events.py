# backend/app/core/events.py
import asyncio
import logging
from typing import Any

from fastapi import FastAPI
from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.redis import close_redis, create_redis_client, redis_health_monitor, startup_redis_health_check
from app.websocket.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


async def startup(app: FastAPI) -> None:
    """Initialise Redis-backed realtime infrastructure."""
    settings = get_settings()
    redis = create_redis_client(settings)
    app.state.redis = redis
    app.state.redis_available = False
    await startup_redis_health_check(app, settings)
    app.state.redis_health_task = asyncio.create_task(redis_health_monitor(app, settings))
    app.state.websocket_manager = ConnectionManager(redis=redis, settings=settings)
    await app.state.websocket_manager.start()
    logger.info("runtime_started", extra={"env": settings.APP_ENV, "redis_available": app.state.redis_available})


async def shutdown(app: FastAPI) -> None:
    """Close background listeners and network clients cleanly."""
    health_task: asyncio.Task[None] | None = getattr(app.state, "redis_health_task", None)
    if health_task is not None:
        health_task.cancel()
        try:
            await health_task
        except asyncio.CancelledError:
            pass
    manager: ConnectionManager | None = getattr(app.state, "websocket_manager", None)
    if manager is not None:
        await manager.stop()
    redis: Redis | None = getattr(app.state, "redis", None)
    await close_redis(redis)
    logger.info("runtime_stopped")


def get_app_state(app: FastAPI) -> dict[str, Any]:
    """Return a small serialisable runtime snapshot for diagnostics."""
    return {
        "has_redis": hasattr(app.state, "redis"),
        "redis_available": bool(getattr(app.state, "redis_available", False)),
        "has_websocket_manager": hasattr(app.state, "websocket_manager"),
    }
