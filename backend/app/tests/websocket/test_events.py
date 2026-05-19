# backend/app/tests/websocket/test_events.py
from types import SimpleNamespace

import pytest

from app.core.config import get_settings
from app.websocket.event_handlers import EventContext, handle_event


class RecordingManager:
    """Minimal broadcaster used by websocket event tests."""

    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict]] = []

    async def broadcast(self, room_id: str, event: str, data: dict) -> None:
        """Record broadcast calls."""
        self.events.append((room_id, event, data))

    async def send_to_user(self, room_id: str, user_id: str, event: str, data: dict) -> None:
        """Record targeted sends."""
        self.events.append((room_id, event, data))

    async def disconnect(self, room_id: str, user_id: str) -> None:
        """Record disconnect calls."""
        self.events.append((room_id, "disconnect", {"user_id": user_id}))


@pytest.mark.asyncio
async def test_websocket_join_start_clue_guess_flow(redis_client) -> None:
    """WebSocket handlers should route events through the registry and game manager."""
    manager = RecordingManager()
    context = EventContext(
        room_id="room-ws",
        user_id="user-1",
        manager=manager,  # type: ignore[arg-type]
        redis=redis_client,
        settings=get_settings(),
    )
    await redis_client.hset("room:membership:room-ws", "user-1", "red:spymaster")
    await handle_event(context, {"event": "join_room", "data": {}})
    await handle_event(context, {"event": "start_game", "data": {"word_pack": "cities", "seed": "ws-seed"}})
    await handle_event(context, {"event": "give_clue", "data": {"word": "travel", "number": 1}})
    await redis_client.hset("room:membership:room-ws", "user-1", "red:operative")
    state_raw = await redis_client.get("game:state:room-ws")
    assert state_raw is not None
    assert any(event[1] == "game_started" for event in manager.events)
