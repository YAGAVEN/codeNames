# backend/app/core/websocket.py
from redis.asyncio import Redis

from app.core.config import Settings
from app.websocket.connection_manager import ConnectionManager


def create_connection_manager(redis: Redis, settings: Settings) -> ConnectionManager:
    """Factory used by tests and app lifecycle code."""
    return ConnectionManager(redis=redis, settings=settings)
