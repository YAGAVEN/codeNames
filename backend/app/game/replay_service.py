# backend/app/game/replay_service.py
import asyncio
from collections.abc import AsyncIterator
from typing import Any
from uuid import UUID

from app.repositories.chat_repository import ChatRepository
from app.repositories.game_move_repository import GameMoveRepository


class ReplayService:
    """Build and stream structured replay exports from persisted move logs."""

    def __init__(self, moves: GameMoveRepository, chats: ChatRepository) -> None:
        self.moves = moves
        self.chats = chats

    async def export(self, game_id: UUID, room_id: UUID, board: list[dict[str, Any]]) -> dict[str, Any]:
        """Return replay JSON containing board, moves, and chat."""
        moves = await self.moves.list_by_game(game_id)
        chats = await self.chats.list_by_room(room_id)
        return {
            "board": board,
            "moves": moves,
            "chat": [
                {
                    "id": str(chat.id),
                    "sender_id": str(chat.sender_id),
                    "message": chat.message,
                    "type": chat.type,
                    "created_at": chat.created_at.isoformat(),
                }
                for chat in chats
            ],
        }

    async def stream(self, replay: dict[str, Any], speed: float = 1.0) -> AsyncIterator[dict[str, Any]]:
        """Yield replay moves with configurable playback speed."""
        delay = max(0.1, 1.0 / max(speed, 0.1))
        for move in replay["moves"]:
            yield {"event": "replay_move", "data": move}
            await asyncio.sleep(delay)
