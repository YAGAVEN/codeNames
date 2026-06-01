# backend/app/game/timer_manager.py
import asyncio
import logging
from typing import Any
from uuid import UUID

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import Settings
from app.core.redis import disconnect_redis_pool

logger = logging.getLogger(__name__)


class TimerManager:
    """Redis-backed per-room countdown manager."""

    def __init__(self, redis: Redis, settings: Settings, broadcaster: Any) -> None:
        self.redis = redis
        self.settings = settings
        self.broadcaster = broadcaster
        self._tasks: dict[str, asyncio.Task[None]] = {}

    async def start_timer(self, room_id: UUID | str, duration_seconds: int | None = None) -> None:
        """Start or replace a turn timer for a room."""
        key = str(room_id)
        await self.stop_timer(key)
        duration = duration_seconds or self.settings.DEFAULT_TURN_SECONDS
        await self._redis_call("timer_start", "setex", f"game:timer:{key}", duration + 5, duration, room_id=key)
        self._tasks[key] = asyncio.create_task(self._run_countdown(key, duration))

    async def stop_timer(self, room_id: UUID | str) -> None:
        """Stop a running room timer if present."""
        key = str(room_id)
        task = self._tasks.pop(key, None)
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        await self._redis_call("timer_stop", "delete", f"game:timer:{key}", room_id=key)

    async def _run_countdown(self, room_id: str, duration: int) -> None:
        """Broadcast timer ticks and emit timeout at zero."""
        remaining = duration
        while remaining >= 0:
            await self._redis_call("timer_tick", "set", f"game:timer:{room_id}", remaining, room_id=room_id)
            await self.broadcaster.broadcast(room_id, "timer_update", {"remaining": remaining})
            if remaining == 0:
                await self.broadcaster.broadcast(room_id, "turn_changed", {"reason": "timeout"})
                return
            sleep_for = 1 if remaining <= 10 else min(5, remaining)
            await asyncio.sleep(sleep_for)
            remaining -= sleep_for

    async def _redis_call(self, operation: str, method_name: str, *args: Any, room_id: str) -> Any:
        """Persist timer data best-effort while keeping broadcasts alive."""
        method = getattr(self.redis, method_name)
        try:
            return await method(*args)
        except RedisError:
            logger.warning("timer_redis_operation_failed", extra={"operation": operation, "room_id": room_id}, exc_info=True)
            await disconnect_redis_pool(self.redis)
            return None
