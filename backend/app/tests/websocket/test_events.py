# backend/app/tests/websocket/test_events.py
from uuid import uuid4

import pytest

from app.core.config import get_settings
from app.db.models.room import Room
from app.db.models.room_player import RoomPlayer
from app.db.models.user import User
from app.game.game_manager import GameManager
from app.utils.constants import PlayerRole, Team
from app.websocket.event_handlers import EventContext, handle_event
from app.websocket.room_events import websocket_endpoint


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


class MissingTokenWebSocket:
    """Minimal WebSocket double for auth-close behavior."""

    query_params = {}

    def __init__(self) -> None:
        self.accepted = False
        self.close_code = None

    async def accept(self) -> None:
        self.accepted = True

    async def close(self, code: int) -> None:
        self.close_code = code


@pytest.mark.asyncio
async def test_websocket_missing_token_closes_cleanly() -> None:
    websocket = MissingTokenWebSocket()

    await websocket_endpoint(websocket, "lobby")  # type: ignore[arg-type]

    assert websocket.accepted is True
    assert websocket.close_code == 4001


@pytest.mark.asyncio
async def test_websocket_join_start_clue_guess_flow(db_session) -> None:
    """WebSocket handlers should route events through the registry and game manager."""
    user_id = uuid4()
    room_id = uuid4()
    room_code = "ROOMWS"
    db_session.add(User(id=user_id, username="ws_user", email="ws@example.com"))
    db_session.add(Room(id=room_id, room_code=room_code, host_id=user_id, max_players=8, settings={}, game_state={}))
    db_session.add(RoomPlayer(room_id=room_id, user_id=user_id, team=Team.RED, role=PlayerRole.SPYMASTER))
    await db_session.commit()

    manager = RecordingManager()
    context = EventContext(
        room_id=room_code,
        user_id=str(user_id),
        manager=manager,  # type: ignore[arg-type]
        db=db_session,
        settings=get_settings(),
    )
    await handle_event(context, {"event": "join_room", "data": {}})
    await handle_event(context, {"event": "start_game", "data": {"word_pack": "cities", "seed": "ws-seed"}})
    await handle_event(context, {"event": "give_clue", "data": {"word": "travel", "number": 1}})
    state = await GameManager().load_state(room_code)
    assert state["current_clue"]["word"] == "travel"
    assert any(event[1] == "game_started" for event in manager.events)
