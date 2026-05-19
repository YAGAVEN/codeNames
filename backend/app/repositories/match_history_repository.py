# backend/app/repositories/match_history_repository.py
from uuid import UUID

from sqlalchemy import select

from app.db.models.match_history import MatchHistory
from app.repositories.base import BaseRepository
from app.utils.constants import PlayerRole, Team


class MatchHistoryRepository(BaseRepository[MatchHistory]):
    """Database operations for per-user match history."""

    model = MatchHistory

    async def create(
        self,
        game_id: UUID,
        user_id: UUID,
        team: Team,
        role: PlayerRole,
        is_winner: bool,
        xp_earned: int,
        clues_given: int,
        correct_guesses: int,
    ) -> MatchHistory:
        """Create a player match-history row."""
        row = MatchHistory(
            game_id=game_id,
            user_id=user_id,
            team=team,
            role=role,
            is_winner=is_winner,
            xp_earned=xp_earned,
            clues_given=clues_given,
            correct_guesses=correct_guesses,
        )
        return await self.add(row)

    async def list_for_user(self, user_id: UUID, limit: int, offset: int) -> list[MatchHistory]:
        """List a user's match history."""
        result = await self.session.execute(
            select(MatchHistory)
            .where(MatchHistory.user_id == user_id)
            .order_by(MatchHistory.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
