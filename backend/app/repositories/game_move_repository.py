# backend/app/repositories/game_move_repository.py
from uuid import UUID

from sqlalchemy import select

from app.db.models.game_move import GameMove
from app.repositories.base import BaseRepository
from app.utils.constants import MoveType


class GameMoveRepository(BaseRepository[GameMove]):
    """Database operations for replay moves."""

    model = GameMove

    async def create(self, game_id: UUID, player_id: UUID, move_type: MoveType, payload: dict) -> GameMove:
        """Append a move to the replay log."""
        move = GameMove(game_id=game_id, player_id=player_id, move_type=move_type, payload=payload)
        return await self.add(move)

    async def list_by_game(self, game_id: UUID) -> list[GameMove]:
        """Return ordered moves for replay."""
        result = await self.session.execute(
            select(GameMove).where(GameMove.game_id == game_id).order_by(GameMove.created_at.asc())
        )
        return list(result.scalars().all())
