# backend/app/websocket/connection_manager.py
import asyncio
import json
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import WebSocket
from redis.asyncio import Redis

from app.core.config import Settings


class ConnectionManager:
    """Redis-backed WebSocket connection manager with pub/sub fanout."""

    def __init__(self, redis: Redis, settings: Settings) -> None:
        self.redis = redis
        self.settings = settings
        self.source_id = str(uuid4())
        self.connections: dict[str, dict[str, WebSocket]] = defaultdict(dict)
        self._listener_task: asyncio.Task[None] | None = None
        self._heartbeat_task: asyncio.Task[None] | None = None
        self._grace_tasks: dict[tuple[str, str], asyncio.Task[None]] = {}

    async def start(self) -> None:
        """Start Redis pub/sub and heartbeat loops."""
        self._listener_task = asyncio.create_task(self._listen_pubsub())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def stop(self) -> None:
        """Stop background loops and close active sockets."""
        for task in (self._listener_task, self._heartbeat_task):
            if task is not None:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        for room_connections in list(self.connections.values()):
            for websocket in list(room_connections.values()):
                await websocket.close()
        self.connections.clear()

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str) -> None:
        """Accept and register a socket in local memory plus Redis indexes."""
        await websocket.accept()
        self.connections[room_id][user_id] = websocket
        await self.redis.sadd(f"room:players:{room_id}", user_id)
        await self.redis.hset(
            f"ws:room:{room_id}:players",
            user_id,
            json.dumps({"connected_at": datetime.now(UTC).isoformat(), "socket": id(websocket)}),
        )
        await self.redis.setex(
            f"presence:{user_id}",
            300,
            json.dumps({"room_id": room_id, "status": "online", "socket": id(websocket)}),
        )
        grace_key = (room_id, user_id)
        grace_task = self._grace_tasks.pop(grace_key, None)
        if grace_task is not None:
            grace_task.cancel()
        await self.broadcast(room_id, "player_joined", {"user_id": user_id})

    async def disconnect(self, room_id: str, user_id: str) -> None:
        """Unregister a socket and begin reconnection grace handling."""
        self.connections.get(room_id, {}).pop(user_id, None)
        await self.redis.srem(f"room:players:{room_id}", user_id)
        await self.redis.hdel(f"ws:room:{room_id}:players", user_id)
        await self.redis.setex(
            f"presence:{user_id}",
            300,
            json.dumps({"room_id": room_id, "status": "offline", "last_seen": datetime.now(UTC).isoformat()}),
        )
        await self.broadcast(room_id, "player_left", {"user_id": user_id, "grace_seconds": self.settings.ROOM_RECONNECT_GRACE_SECONDS})
        self._grace_tasks[(room_id, user_id)] = asyncio.create_task(self._mark_abandoned_after_grace(room_id, user_id))

    async def broadcast(self, room_id: str, event: str, data: dict[str, Any]) -> None:
        """Publish a room event through Redis and send to local sockets once."""
        message = {"source": self.source_id, "room_id": room_id, "event": event, "data": data}
        await self.redis.publish(f"pub:room:{room_id}", json.dumps(message))
        await self._broadcast_local(room_id, event, data)

    async def send_to_user(self, room_id: str, user_id: str, event: str, data: dict[str, Any]) -> None:
        """Send an event to one connected local user."""
        websocket = self.connections.get(room_id, {}).get(user_id)
        if websocket is not None:
            await websocket.send_json({"event": event, "data": data})

    async def _listen_pubsub(self) -> None:
        """Listen for cross-worker broadcasts from Redis."""
        pubsub = self.redis.pubsub()
        await pubsub.psubscribe("pub:room:*")
        try:
            async for message in pubsub.listen():
                if message.get("type") != "pmessage":
                    continue
                raw = message["data"].decode() if isinstance(message["data"], bytes) else message["data"]
                payload = json.loads(raw)
                if payload.get("source") == self.source_id:
                    continue
                await self._broadcast_local(payload["room_id"], payload["event"], payload["data"])
        finally:
            await pubsub.punsubscribe("pub:room:*")
            await pubsub.close()

    async def _broadcast_local(self, room_id: str, event: str, data: dict[str, Any]) -> None:
        """Send a JSON event to all sockets attached to this worker."""
        stale: list[str] = []
        for user_id, websocket in list(self.connections.get(room_id, {}).items()):
            try:
                await websocket.send_json({"event": event, "data": data})
            except RuntimeError:
                stale.append(user_id)
        for user_id in stale:
            await self.disconnect(room_id, user_id)

    async def _heartbeat_loop(self) -> None:
        """Send heartbeats and drop dead sockets after failed writes."""
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
        await asyncio.sleep(self.settings.ROOM_RECONNECT_GRACE_SECONDS)
        if user_id not in self.connections.get(room_id, {}):
            await self.broadcast(room_id, "player_left", {"user_id": user_id, "abandoned": True})
