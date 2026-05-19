# backend/app/services/match_service.py
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.game.replay_service import ReplayService
from app.repositories.chat_repository import ChatRepository
from app.repositories.game_move_repository import GameMoveRepository
from app.repositories.game_repository import GameRepository
from app.repositories.match_history_repository import MatchHistoryRepository
from app.utils.exceptions import NotFoundError


class MatchService:
    """Match history and replay orchestration."""

    def __init__(self, session: AsyncSession) -> None:
        self.games = GameRepository(session)
        self.history = MatchHistoryRepository(session)
        self.moves = GameMoveRepository(session)
        self.chats = ChatRepository(session)

    async def history_for_user(self, user_id: UUID, page: int, per_page: int) -> list[object]:
        """Return match history rows for a user."""
        return await self.history.list_for_user(user_id, per_page, (page - 1) * per_page)

    async def get_match(self, game_id: UUID) -> object:
        """Return a game summary."""
        game = await self.games.get(game_id)
        if game is None:
            raise NotFoundError("Game not found")
        return game

    async def replay(self, game_id: UUID) -> dict:
        """Return replay export for a game."""
        game = await self.games.get(game_id)
        if game is None:
            raise NotFoundError("Game not found")
        board = game.replay_data.get("board", [])
        return await ReplayService(self.moves, self.chats).export(game_id, game.room_id, board)
