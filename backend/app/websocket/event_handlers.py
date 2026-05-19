# backend/app/websocket/event_handlers.py
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from redis.asyncio import Redis

from app.core.config import Settings
from app.game.game_manager import GameManager
from app.game.word_service import WordService
from app.schemas.websocket import ClientEvent
from app.utils.constants import ChatType, PlayerRole, Team
from app.utils.exceptions import AppError, GameRuleError
from app.utils.validators import sanitise_chat_message
from app.websocket.connection_manager import ConnectionManager


@dataclass(frozen=True)
class EventContext:
    """Context passed to typed WebSocket event handlers."""

    room_id: str
    user_id: str
    manager: ConnectionManager
    redis: Redis
    settings: Settings


Handler = Callable[[EventContext, dict[str, Any]], Awaitable[None]]
HANDLERS: dict[str, Handler] = {}


def websocket_handler(event_name: str) -> Callable[[Handler], Handler]:
    """Register a WebSocket handler without a giant if/elif chain."""

    def decorator(func: Handler) -> Handler:
        HANDLERS[event_name] = func
        return func

    return decorator


async def handle_event(context: EventContext, payload: dict[str, Any]) -> None:
    """Validate and dispatch a client event."""
    event = ClientEvent.model_validate(payload)
    handler = HANDLERS.get(event.event)
    if handler is None:
        raise GameRuleError(f"Unsupported event '{event.event}'")
    await handler(context, event.data)


async def _membership(context: EventContext) -> tuple[Team, PlayerRole]:
    """Read server-stored team and role for the connected user."""
    raw = await context.redis.hget(f"room:membership:{context.room_id}", context.user_id)
    if raw is None:
        return Team.SPECTATOR, PlayerRole.OPERATIVE
    data = raw.decode() if isinstance(raw, bytes) else raw
    team, role = data.split(":", 1)
    return Team(team), PlayerRole(role)


@websocket_handler("create_room")
async def create_room(context: EventContext, data: dict[str, Any]) -> None:
    """Broadcast a room-created event for realtime lobby clients."""
    await context.manager.broadcast(context.room_id, "room_created", {"room_id": context.room_id, "host_id": context.user_id})


@websocket_handler("join_room")
async def join_room(context: EventContext, data: dict[str, Any]) -> None:
    """Join room presence and store realtime membership metadata."""
    raw = await context.redis.hget(f"room:membership:{context.room_id}", context.user_id)
    if raw is None:
        # A trusted REST join/team-assignment path should set this hash; unknown users become spectators.
        team = Team.SPECTATOR
        role = PlayerRole.OPERATIVE
        await context.redis.hset(f"room:membership:{context.room_id}", context.user_id, f"{team.value}:{role.value}")
    else:
        stored = raw.decode() if isinstance(raw, bytes) else raw
        team_value, role_value = stored.split(":", 1)
        team = Team(team_value)
        role = PlayerRole(role_value)
    await context.manager.broadcast(context.room_id, "player_joined", {"user_id": context.user_id, "team": team.value, "role": role.value})


@websocket_handler("leave_room")
async def leave_room(context: EventContext, data: dict[str, Any]) -> None:
    """Leave a room voluntarily."""
    await context.manager.disconnect(context.room_id, context.user_id)


@websocket_handler("ready_up")
async def ready_up(context: EventContext, data: dict[str, Any]) -> None:
    """Mark a player ready in Redis for fast lobby checks."""
    ready = bool(data.get("is_ready", True))
    await context.redis.hset(f"room:ready:{context.room_id}", context.user_id, "1" if ready else "0")
    await context.manager.broadcast(context.room_id, "player_joined", {"user_id": context.user_id, "is_ready": ready})


@websocket_handler("start_game")
async def start_game(context: EventContext, data: dict[str, Any]) -> None:
    """Start a new server-authoritative game state."""
    pack_name = str(data.get("word_pack", "cities"))
    seed = str(data.get("seed") or uuid4())
    words = await WordService(context.redis, context.settings).load_word_pack(pack_name)
    state = await GameManager(context.redis).start_game(context.room_id, words, seed, pack_name)
    public_board = [{"index": card["index"], "word": card["word"], "revealed": card["revealed"]} for card in state["board"]]
    await context.manager.broadcast(context.room_id, "game_started", {"room_id": context.room_id, "seed": seed})
    await context.manager.broadcast(context.room_id, "board_updated", {"board": public_board})


@websocket_handler("give_clue")
async def give_clue(context: EventContext, data: dict[str, Any]) -> None:
    """Apply a clue from the current team's spymaster."""
    team, role = await _membership(context)
    state = await GameManager(context.redis).give_clue(
        context.room_id,
        context.user_id,
        team,
        role,
        str(data["word"]),
        int(data["number"]),
    )
    await context.manager.broadcast(context.room_id, "clue_received", {"clue": state["current_clue"], "team": team.value})


@websocket_handler("select_card")
async def select_card(context: EventContext, data: dict[str, Any]) -> None:
    """Apply an operative guess and broadcast board/score updates."""
    team, role = await _membership(context)
    card_index = int(data["card_index"])
    state = await GameManager(context.redis).select_card(context.room_id, context.user_id, team, role, card_index)
    card = state["board"][card_index]
    await context.manager.broadcast(context.room_id, "card_revealed", {"card": card})
    await context.manager.broadcast(context.room_id, "score_updated", {"scores": state["scores"]})
    if state["status"] == "finished":
        await context.manager.broadcast(context.room_id, "game_over", {"winner_team": state["winner_team"]})
    else:
        await context.manager.broadcast(context.room_id, "turn_changed", {"current_team": state["current_team"]})


@websocket_handler("end_turn")
async def end_turn(context: EventContext, data: dict[str, Any]) -> None:
    """Pass the current team's turn."""
    team, _ = await _membership(context)
    state = await GameManager(context.redis).end_turn(context.room_id, context.user_id, team)
    await context.manager.broadcast(context.room_id, "turn_changed", {"current_team": state["current_team"]})


@websocket_handler("send_chat")
async def send_chat(context: EventContext, data: dict[str, Any]) -> None:
    """Broadcast a sanitised chat message."""
    message = sanitise_chat_message(str(data.get("message", "")))
    chat_type = ChatType(data.get("type", ChatType.ROOM.value))
    if not message:
        raise GameRuleError("Chat message cannot be empty")
    await context.manager.broadcast(
        context.room_id,
        "chat_message",
        {"sender_id": context.user_id, "message": message, "type": chat_type.value},
    )


@websocket_handler("typing")
async def typing(context: EventContext, data: dict[str, Any]) -> None:
    """Broadcast lightweight typing presence."""
    await context.manager.broadcast(context.room_id, "chat_message", {"sender_id": context.user_id, "typing": bool(data.get("typing", True))})


@websocket_handler("reaction")
async def reaction(context: EventContext, data: dict[str, Any]) -> None:
    """Broadcast a small room reaction."""
    await context.manager.broadcast(context.room_id, "chat_message", {"sender_id": context.user_id, "reaction": str(data.get("reaction", ""))[:32]})


@websocket_handler("reconnect_player")
async def reconnect_player(context: EventContext, data: dict[str, Any]) -> None:
    """Confirm reconnection after grace timer cancellation."""
    await context.manager.send_to_user(context.room_id, context.user_id, "reconnect_success", {"room_id": context.room_id})


@websocket_handler("spectate_game")
async def spectate_game(context: EventContext, data: dict[str, Any]) -> None:
    """Move a user into spectator presence."""
    await context.redis.hset(f"room:membership:{context.room_id}", context.user_id, f"{Team.SPECTATOR.value}:{PlayerRole.OPERATIVE.value}")
    await context.manager.broadcast(context.room_id, "player_joined", {"user_id": context.user_id, "team": Team.SPECTATOR.value})


async def send_event_error(context: EventContext, exc: Exception) -> None:
    """Send a standard error event to one socket."""
    code = exc.code if isinstance(exc, AppError) else "websocket_error"
    message = exc.message if isinstance(exc, AppError) else "Unexpected websocket error"
    await context.manager.send_to_user(context.room_id, context.user_id, "error_message", {"code": code, "message": message})
