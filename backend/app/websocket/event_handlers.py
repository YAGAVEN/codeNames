# backend/app/websocket/event_handlers.py
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.game.game_manager import GameManager
from app.game.word_service import WordService
from app.repositories.room_player_repository import RoomPlayerRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.user_repository import UserRepository
from app.schemas.websocket import ClientEvent
from app.utils.constants import ChatType, PlayerRole, RoomStatus, Team
from app.utils.exceptions import AppError, AuthorizationError, GameRuleError
from app.utils.validators import sanitise_chat_message
from app.websocket.connection_manager import ConnectionManager


@dataclass(frozen=True)
class EventContext:
    """Context passed to typed WebSocket event handlers."""

    room_id: str
    user_id: str
    manager: ConnectionManager
    db: AsyncSession
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
    await _touch_room_activity(context)
    await handler(context, event.data)


async def _touch_room_activity(context: EventContext) -> None:
    """Persist recent room activity for cleanup decisions."""
    room_id = await _room_uuid(context)
    if room_id is None:
        return
    repo = RoomRepository(context.db)
    touched = await repo.touch_activity(room_id)
    if touched is not None:
        await repo.commit()


async def _membership(context: EventContext) -> tuple[Team, PlayerRole]:
    """Read server-stored team and role for the connected user."""
    room_id = await _room_uuid(context)
    user_id = _user_uuid(context.user_id)
    if room_id is None or user_id is None:
        return Team.SPECTATOR, PlayerRole.OPERATIVE
    membership = await RoomPlayerRepository(context.db).get_membership(room_id, user_id)
    if membership is None:
        return Team.SPECTATOR, PlayerRole.OPERATIVE
    return membership.team, membership.role


async def _get_username(context: EventContext) -> str:
    """Fetch the display username for the current connected user."""
    user_id = _user_uuid(context.user_id)
    if user_id is None:
        return f"Player {context.user_id[:6]}"
    try:
        user_repo = UserRepository(context.db)
        user = await user_repo.get(user_id)
        if user is not None and user.username:
            return user.username
    except Exception:
        pass
    return f"Player {context.user_id[:6]}"


def _public_card(card: dict[str, Any]) -> dict[str, Any]:
    """Hide unrevealed card ownership from operative clients."""
    payload = {
        "index": card["index"],
        "word": card["word"],
        "revealed": card["revealed"],
    }
    if card["revealed"]:
        payload["team"] = card["team"]
        payload["type"] = card["team"]
        payload["revealed_by"] = card.get("revealed_by")
    return payload


def _full_card(card: dict[str, Any]) -> dict[str, Any]:
    """Return the full card payload for authorized spymaster clients."""
    return {
        "index": card["index"],
        "word": card["word"],
        "team": card["team"],
        "type": card["team"],
        "revealed": card["revealed"],
        "revealed_by": card.get("revealed_by"),
    }


def _score_payload(state: dict[str, Any]) -> dict[str, Any]:
    """Build score data with found counts and totals."""
    board = state["board"]
    return {
        "red": state["scores"][Team.RED.value],
        "blue": state["scores"][Team.BLUE.value],
        "neutral": sum(1 for card in board if card["team"] == "neutral" and card["revealed"]),
        "assassinRevealed": any(card["team"] == "assassin" and card["revealed"] for card in board),
        "redTotal": sum(1 for card in board if card["team"] == Team.RED.value),
        "blueTotal": sum(1 for card in board if card["team"] == Team.BLUE.value),
    }


def _public_state(state: dict[str, Any]) -> dict[str, Any]:
    """Return the server-authoritative game state safe for all players."""
    return {
        "room_id": state["room_id"],
        "status": state["status"],
        "seed": state["seed"],
        "word_pack": state["word_pack"],
        "board": [_public_card(card) for card in state["board"]],
        "current_team": state["current_team"],
        "current_clue": state["current_clue"],
        "scores": _score_payload(state),
        "winner_team": state["winner_team"],
    }


async def _send_spymaster_board(context: EventContext, state: dict[str, Any]) -> None:
    """Send the hidden board only to sockets cached as spymasters."""
    room_id = await _room_uuid(context)
    if room_id is None:
        return
    memberships = await RoomPlayerRepository(context.db).list_by_room(room_id)
    for membership, _ in memberships:
        if membership.role == PlayerRole.SPYMASTER:
            await context.manager.send_to_user(
                context.room_id,
                str(membership.user_id),
                "spymaster_board_updated",
                {"board": [_full_card(card) for card in state["board"]]},
            )


@websocket_handler("create_room")
async def create_room(context: EventContext, data: dict[str, Any]) -> None:
    """Broadcast a room-created event for realtime lobby clients."""
    await context.manager.broadcast(context.room_id, "room_created", {"room_id": context.room_id, "host_id": context.user_id})


@websocket_handler("join_room")
async def join_room(context: EventContext, data: dict[str, Any]) -> None:
    """Join room presence and broadcast full player info to all connected clients.

    This is the authoritative player_joined broadcast — it includes the username
    so all clients can display the correct player name immediately.
    """
    team, role = await _membership(context)
    username = await _get_username(context)

    # Broadcast full player info to everyone in the room (including the joining player).
    await context.manager.broadcast(
        context.room_id,
        "player_joined",
        {
            "user_id": context.user_id,
            "username": username,
            "name": username,
            "team": team.value,
            "role": role.value,
        },
    )

    # If a game is already in progress, send the current state to the late-joining player.
    try:
        state = await GameManager().load_state(context.room_id)
    except GameRuleError:
        return
    public_state = _public_state(state)
    await context.manager.send_to_user(context.room_id, context.user_id, "game_started", public_state)
    if role == PlayerRole.SPYMASTER:
        await context.manager.send_to_user(
            context.room_id,
            context.user_id,
            "spymaster_board_updated",
            {"board": [_full_card(card) for card in state["board"]]},
        )


@websocket_handler("leave_room")
async def leave_room(context: EventContext, data: dict[str, Any]) -> None:
    """Leave a room voluntarily."""
    await context.manager.disconnect(context.room_id, context.user_id)


@websocket_handler("change_team")
async def change_team(context: EventContext, data: dict[str, Any]) -> None:
    """Allow a player to switch teams before the game starts.

    Validates the room is in waiting state, updates the DB membership,
    then broadcasts the new team assignment to all connected clients.
    """
    room_id = await _room_uuid(context)
    user_id = _user_uuid(context.user_id)
    if room_id is None or user_id is None:
        raise GameRuleError("Invalid room or user")

    # Validate request team value
    raw_team = str(data.get("team", "")).lower()
    try:
        new_team = Team(raw_team)
    except ValueError:
        raise GameRuleError(f"Invalid team '{raw_team}'. Must be 'red', 'blue', or 'spectator'")

    # Ensure the room is still in lobby (waiting) state
    room_repo = RoomRepository(context.db)
    room = await room_repo.get(room_id)
    if room is None:
        raise GameRuleError("Room not found")
    if room.status != RoomStatus.WAITING:
        raise GameRuleError("Team changes are not allowed once the game has started")

    # Update DB and get new membership details
    player_repo = RoomPlayerRepository(context.db)
    membership = await player_repo.set_team(room_id, user_id, new_team)
    if membership is None:
        raise GameRuleError("You are not a member of this room")
    await player_repo.commit()

    username = await _get_username(context)

    # Broadcast the team change to ALL connected clients
    await context.manager.broadcast(
        context.room_id,
        "team_changed",
        {
            "user_id": context.user_id,
            "username": username,
            "name": username,
            "team": membership.team.value,
            "role": membership.role.value,
        },
    )


@websocket_handler("ready_up")
async def ready_up(context: EventContext, data: dict[str, Any]) -> None:
    """Mark a player ready in the database."""
    ready = bool(data.get("is_ready", True))
    room_id = await _room_uuid(context)
    user_id = _user_uuid(context.user_id)
    if room_id is not None and user_id is not None:
        repo = RoomPlayerRepository(context.db)
        await repo.set_ready(room_id, user_id, ready)
        await repo.commit()
    await context.manager.broadcast(context.room_id, "player_joined", {"user_id": context.user_id, "is_ready": ready})


@websocket_handler("start_game")
async def start_game(context: EventContext, data: dict[str, Any]) -> None:
    """Start a new server-authoritative game state.

    Only the room host (admin) may call this. The server validates
    the requester's user_id against the room.host_id before proceeding.
    """
    room_id = await _room_uuid(context)
    if room_id is None:
        raise GameRuleError("Invalid room")

    # ── Admin check ──────────────────────────────────────────────────────────
    room_repo = RoomRepository(context.db)
    room = await room_repo.get(room_id)
    if room is None:
        raise GameRuleError("Room not found")
    if str(room.host_id) != context.user_id:
        raise AuthorizationError("Only the room admin can start the game")
    # ─────────────────────────────────────────────────────────────────────────

    pack_name = str(data.get("word_pack", "india"))
    seed = str(data.get("seed") or uuid4())

    # Load word pack with graceful fallback so a missing Supabase pack never
    # prevents the game from starting.
    try:
        words = await WordService(context.settings).load_word_pack(pack_name)
    except Exception:
        from app.game.word_service import DEFAULT_WORDS
        words = list(DEFAULT_WORDS)

    state = await GameManager().start_game(context.room_id, words, seed, pack_name)
    room.status = RoomStatus.IN_PROGRESS
    room.game_state = state
    await room_repo.commit()
    public = _public_state(state)
    await context.manager.broadcast(context.room_id, "game_started", public)
    await context.manager.broadcast(context.room_id, "board_updated", {"board": public["board"], "scores": _score_payload(state)})
    await _send_spymaster_board(context, state)


@websocket_handler("give_clue")
async def give_clue(context: EventContext, data: dict[str, Any]) -> None:
    """Apply a clue from the current team's spymaster."""
    team, role = await _membership(context)
    state = await GameManager().give_clue(
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
    state = await GameManager().select_card(context.room_id, context.user_id, team, role, card_index)
    card = state["board"][card_index]
    await context.manager.broadcast(context.room_id, "card_revealed", {"card": _full_card(card)})
    await context.manager.broadcast(context.room_id, "score_updated", {"scores": _score_payload(state)})
    await _send_spymaster_board(context, state)
    if state["status"] == "finished":
        await context.manager.broadcast(context.room_id, "game_over", {"winner_team": state["winner_team"]})
    else:
        await context.manager.broadcast(context.room_id, "turn_changed", {"current_team": state["current_team"]})


@websocket_handler("end_turn")
async def end_turn(context: EventContext, data: dict[str, Any]) -> None:
    """Pass the current team's turn."""
    team, _ = await _membership(context)
    state = await GameManager().end_turn(context.room_id, context.user_id, team)
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
    room_id = await _room_uuid(context)
    user_id = _user_uuid(context.user_id)
    if room_id is not None and user_id is not None:
        repo = RoomPlayerRepository(context.db)
        membership = await repo.get_membership(room_id, user_id)
        if membership is not None:
            membership.team = Team.SPECTATOR
            membership.role = PlayerRole.OPERATIVE
            await repo.commit()
    await context.manager.broadcast(context.room_id, "player_joined", {"user_id": context.user_id, "team": Team.SPECTATOR.value})


async def send_event_error(context: EventContext, exc: Exception) -> None:
    """Send a standard error event to one socket."""
    code = exc.code if isinstance(exc, AppError) else "websocket_error"
    message = exc.message if isinstance(exc, AppError) else "Unexpected websocket error"
    await context.manager.send_to_user(context.room_id, context.user_id, "error_message", {"code": code, "message": message})


async def _room_uuid(context: EventContext) -> UUID | None:
    """Resolve the WebSocket room path as either UUID or public room code."""
    try:
        return UUID(context.room_id)
    except ValueError:
        room = await RoomRepository(context.db).get_by_code(context.room_id.upper())
        return room.id if room is not None else None


def _user_uuid(user_id: str) -> UUID | None:
    """Parse a user id from an access token payload."""
    try:
        return UUID(user_id)
    except ValueError:
        return None
