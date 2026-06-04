# backend/app/schemas/websocket.py
from typing import Any, Literal

from pydantic import Field

from app.schemas.common import StrictSchema

ClientEventName = Literal[
    "create_room",
    "join_room",
    "leave_room",
    "ready_up",
    "change_team",
    "start_game",
    "give_clue",
    "select_card",
    "end_turn",
    "send_chat",
    "typing",
    "reaction",
    "reconnect_player",
    "spectate_game",
]

ServerEventName = Literal[
    "room_created",
    "player_joined",
    "player_left",
    "team_changed",
    "game_started",
    "turn_changed",
    "clue_received",
    "board_updated",
    "spymaster_board_updated",
    "card_revealed",
    "score_updated",
    "game_over",
    "timer_update",
    "reconnect_success",
    "chat_message",
    "error_message",
]


class ClientEvent(StrictSchema):
    """Client-to-server WebSocket event envelope."""

    event: ClientEventName
    data: dict[str, Any] = Field(default_factory=dict)


class ServerEvent(StrictSchema):
    """Server-to-client WebSocket event envelope."""

    event: ServerEventName
    data: dict[str, Any] = Field(default_factory=dict)
