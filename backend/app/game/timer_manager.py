# backend/app/game/timer_manager.py
import asyncio
from typing import Any
from uuid import UUID

from app.core.config import Settings


class TimerManager:
    """In-memory per-room countdown manager."""

    def __init__(self, settings: Settings, broadcaster: Any) -> None:
        self.settings = settings
        self.broadcaster = broadcaster
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._timers: dict[str, int] = {}

    async def start_timer(self, room_id: UUID | str, duration_seconds: int | None = None) -> None:
        """Start or replace a turn timer for a room."""
        key = str(room_id)
        await self.stop_timer(key)
        duration = duration_seconds or self.settings.DEFAULT_TURN_SECONDS
        self._timers[key] = duration
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
        self._timers.pop(key, None)

    async def _run_countdown(self, room_id: str, duration: int) -> None:
        """Broadcast timer ticks and emit timeout at zero."""
        remaining = duration
        while remaining >= 0:
            self._timers[room_id] = remaining
            await self.broadcaster.broadcast(room_id, "timer_update", {"remaining": remaining})
            if remaining == 0:
                await self.broadcaster.broadcast(room_id, "turn_changed", {"reason": "timeout"})
                self._timers.pop(room_id, None)
                return
            sleep_for = 1 if remaining <= 10 else min(5, remaining)
            await asyncio.sleep(sleep_for)
            remaining -= sleep_for
