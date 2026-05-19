# backend/app/repositories/game_repository.py
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select

from app.db.models.game import Game
from app.repositories.base import BaseRepository
from app.utils.constants import Team


class GameRepository(BaseRepository[Game]):
    """Database operations for games."""

    model = Game

    async def create(self, room_id: UUID, word_pack: str, replay_data: dict | None = None) -> Game:
        """Create a new game row."""
        game = Game(room_id=room_id, word_pack=word_pack, replay_data=replay_data or {}, started_at=datetime.now(UTC))
        return await self.add(game)

    async def finish(self, game: Game, winner_team: Team | None, red_score: int, blue_score: int, replay_data: dict) -> Game:
        """Finalize a game summary."""
        game.winner_team = winner_team
        game.red_score = red_score
        game.blue_score = blue_score
        game.replay_data = replay_data
        game.ended_at = datetime.now(UTC)
        if game.started_at:
            game.duration_seconds = int((game.ended_at - game.started_at).total_seconds())
        await self.session.flush()
        return game

    async def count(self) -> int:
        """Count all games."""
        result = await self.session.execute(select(func.count()).select_from(Game))
        return int(result.scalar_one())
