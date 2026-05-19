# backend/app/websocket/room_events.py
from typing import Any

from fastapi import WebSocket

from app.core.security import decode_token
from app.utils.exceptions import AuthenticationError
from app.websocket.event_handlers import EventContext, handle_event, send_event_error


async def websocket_endpoint(websocket: WebSocket, room_id: str) -> None:
    """Authenticate a room socket and process typed client events."""
    token = websocket.query_params.get("token")
    try:
        if token is None:
            first_message: dict[str, Any] = await websocket.receive_json()
            if first_message.get("event") != "auth":
                raise AuthenticationError("First WebSocket message must authenticate")
            token = str(first_message.get("data", {}).get("token", ""))
        payload = decode_token(token)
    except AuthenticationError:
        await websocket.close(code=4001)
        return

    user_id = str(payload["sub"])
    manager = websocket.app.state.websocket_manager
    redis = websocket.app.state.redis
    settings = manager.settings
    context = EventContext(room_id=room_id, user_id=user_id, manager=manager, redis=redis, settings=settings)
    await manager.connect(websocket, room_id, user_id)
    try:
        while True:
            message = await websocket.receive_json()
            try:
                await handle_event(context, message)
            except Exception as exc:
                await send_event_error(context, exc)
    except Exception:
        await manager.disconnect(room_id, user_id)
