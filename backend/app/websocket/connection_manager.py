# backend/app/websocket/connection_manager.py
import asyncio
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import WebSocket

from app.core.config import Settings


class ConnectionManager:
    """Single-process WebSocket connection manager."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.source_id = str(uuid4())
        self.connections: dict[str, dict[str, WebSocket]] = defaultdict(dict)
        self._heartbeat_task: asyncio.Task[None] | None = None
        self._grace_tasks: dict[tuple[str, str], asyncio.Task[None]] = {}

    async def start(self) -> None:
        """Start background heartbeat handling."""
        if self._heartbeat_task is None:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def stop(self) -> None:
        """Stop background loops and close active sockets."""
        tasks = [task for task in [self._heartbeat_task, *self._grace_tasks.values()] if task is not None]
        for task in tasks:
            task.cancel()
        for task in tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass
        for room_connections in list(self.connections.values()):
            for websocket in list(room_connections.values()):
                await websocket.close()
        self.connections.clear()
        self._grace_tasks.clear()
        self._heartbeat_task = None

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str) -> None:
        """Accept and register a socket in local memory.

        NOTE: Does NOT broadcast player_joined here. The join_room WS event
        handler performs the broadcast with full user info (username, team, role).
        """
        await websocket.accept()
        self.connections[room_id][user_id] = websocket
        grace_key = (room_id, user_id)
        grace_task = self._grace_tasks.pop(grace_key, None)
        if grace_task is not None:
            grace_task.cancel()

    async def disconnect(self, room_id: str, user_id: str) -> None:
        """Unregister a socket and begin reconnection grace handling."""
        self.connections.get(room_id, {}).pop(user_id, None)
        await self.broadcast(room_id, "player_left", {"user_id": user_id, "grace_seconds": self.settings.ROOM_RECONNECT_GRACE_SECONDS})
        grace_key = (room_id, user_id)
        previous = self._grace_tasks.pop(grace_key, None)
        if previous is not None:
            previous.cancel()
        self._grace_tasks[grace_key] = asyncio.create_task(self._mark_abandoned_after_grace(room_id, user_id))

    async def broadcast(self, room_id: str, event: str, data: dict[str, Any]) -> None:
        """Send a JSON event to all sockets attached to this worker."""
        stale: list[str] = []
        for user_id, websocket in list(self.connections.get(room_id, {}).items()):
            try:
                await websocket.send_json({"event": event, "data": data})
            except RuntimeError:
                stale.append(user_id)
        for user_id in stale:
            self.connections.get(room_id, {}).pop(user_id, None)

    async def send_to_user(self, room_id: str, user_id: str, event: str, data: dict[str, Any]) -> None:
        """Send an event to one connected local user."""
        websocket = self.connections.get(room_id, {}).get(user_id)
        if websocket is not None:
            await websocket.send_json({"event": event, "data": data})

    async def _heartbeat_loop(self) -> None:
        """Send heartbeats and disconnect dead sockets."""
        while True:
            await asyncio.sleep(self.settings.WS_HEARTBEAT_SECONDS)
            for room_id, room_connections in list(self.connections.items()):
                for user_id, websocket in list(room_connections.items()):
                    try:
                        await websocket.send_json({"event": "heartbeat", "data": {"ts": datetime.now(UTC).isoformat()}})
                    except RuntimeError:
                        await self.disconnect(room_id, user_id)

    async def _mark_abandoned_after_grace(self, room_id: str, user_id: str) -> None:
        """Broadcast abandoned state if a player does not reconnect in time."""
        try:
            await asyncio.sleep(self.settings.ROOM_RECONNECT_GRACE_SECONDS)
            if user_id not in self.connections.get(room_id, {}):
                await self.broadcast(room_id, "player_left", {"user_id": user_id, "abandoned": True})
        finally:
            self._grace_tasks.pop((room_id, user_id), None)
