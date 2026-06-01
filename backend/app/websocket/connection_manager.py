# backend/app/websocket/connection_manager.py
import asyncio
import json
import logging
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import WebSocket
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import Settings
from app.core.redis import disconnect_redis_pool

logger = logging.getLogger(__name__)


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
        await self._redis_call("sadd_room_player", "sadd", f"room:players:{room_id}", user_id, room_id=room_id, user_id=user_id)
        await self._redis_call(
            "hset_room_player",
            "hset",
            f"ws:room:{room_id}:players",
            user_id,
            json.dumps({"connected_at": datetime.now(UTC).isoformat(), "socket": id(websocket)}),
            room_id=room_id,
            user_id=user_id,
        )
        await self._redis_call(
            "set_presence_online",
            "setex",
            f"presence:{user_id}",
            300,
            json.dumps({"room_id": room_id, "status": "online", "socket": id(websocket)}),
            room_id=room_id,
            user_id=user_id,
        )
        grace_key = (room_id, user_id)
        grace_task = self._grace_tasks.pop(grace_key, None)
        if grace_task is not None:
            grace_task.cancel()
        await self.broadcast(room_id, "player_joined", {"user_id": user_id})

    async def disconnect(self, room_id: str, user_id: str) -> None:
        """Unregister a socket and begin reconnection grace handling."""
        self.connections.get(room_id, {}).pop(user_id, None)
        await self._redis_call("srem_room_player", "srem", f"room:players:{room_id}", user_id, room_id=room_id, user_id=user_id)
        await self._redis_call("hdel_room_player", "hdel", f"ws:room:{room_id}:players", user_id, room_id=room_id, user_id=user_id)
        await self._redis_call(
            "set_presence_offline",
            "setex",
            f"presence:{user_id}",
            300,
            json.dumps({"room_id": room_id, "status": "offline", "last_seen": datetime.now(UTC).isoformat()}),
            room_id=room_id,
            user_id=user_id,
        )
        await self.broadcast(room_id, "player_left", {"user_id": user_id, "grace_seconds": self.settings.ROOM_RECONNECT_GRACE_SECONDS})
        self._grace_tasks[(room_id, user_id)] = asyncio.create_task(self._mark_abandoned_after_grace(room_id, user_id))

    async def broadcast(self, room_id: str, event: str, data: dict[str, Any]) -> None:
        """Publish a room event through Redis and send to local sockets once."""
        message = {"source": self.source_id, "room_id": room_id, "event": event, "data": data}
        await self._redis_call("publish_room_event", "publish", f"pub:room:{room_id}", json.dumps(message), room_id=room_id, event=event)
        await self._broadcast_local(room_id, event, data)

    async def send_to_user(self, room_id: str, user_id: str, event: str, data: dict[str, Any]) -> None:
        """Send an event to one connected local user."""
        websocket = self.connections.get(room_id, {}).get(user_id)
        if websocket is not None:
            await websocket.send_json({"event": event, "data": data})

    async def _listen_pubsub(self) -> None:
        """Listen for cross-worker broadcasts from Redis."""
        while True:
            pubsub = None
            try:
                pubsub = self.redis.pubsub()
                await pubsub.psubscribe("pub:room:*")
                logger.info("websocket_pubsub_connected")
                async for message in pubsub.listen():
                    if message.get("type") != "pmessage":
                        continue
                    raw = message["data"].decode() if isinstance(message["data"], bytes) else message["data"]
                    payload = json.loads(raw)
                    if payload.get("source") == self.source_id:
                        continue
                    await self._broadcast_local(payload["room_id"], payload["event"], payload["data"])
            except asyncio.CancelledError:
                raise
            except RedisError:
                logger.warning("websocket_pubsub_redis_unavailable", exc_info=True)
                await disconnect_redis_pool(self.redis)
                await asyncio.sleep(self.settings.REDIS_RECONNECT_INTERVAL_SECONDS)
            except Exception:
                logger.exception("websocket_pubsub_listener_failed")
                await asyncio.sleep(self.settings.REDIS_RECONNECT_INTERVAL_SECONDS)
            finally:
                if pubsub is not None:
                    try:
                        await pubsub.punsubscribe("pub:room:*")
                        close = getattr(pubsub, "aclose", None) or pubsub.close
                        await close()
                    except RedisError:
                        logger.debug("websocket_pubsub_close_failed", exc_info=True)

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

    async def _redis_call(self, operation: str, method_name: str, *args: Any, **context: Any) -> Any:
        """Run a Redis operation as best-effort so realtime local delivery survives outages."""
        method = getattr(self.redis, method_name)
        try:
            return await method(*args)
        except RedisError:
            logger.warning(
                "websocket_redis_operation_failed",
                extra={"operation": operation, **context},
                exc_info=True,
            )
            await disconnect_redis_pool(self.redis)
            return None
