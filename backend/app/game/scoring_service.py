# backend/app/game/scoring_service.py
from dataclasses import dataclass
from uuid import UUID

from app.repositories.match_history_repository import MatchHistoryRepository
from app.repositories.user_repository import UserRepository
from app.utils.constants import PlayerRole, Team


@dataclass(frozen=True)
class PlayerStats:
    """Stats needed to score a player's completed match."""

    user_id: UUID
    team: Team
    role: PlayerRole
    correct_guesses: int = 0
    wrong_guesses: int = 0
    clues_given: int = 0
    streak: int = 0


class ScoringService:
    """XP, rank, MVP, and match-history scoring logic."""

    def calculate_xp(self, correct_guesses: int, streak: int, base_xp: int = 50) -> int:
        """Calculate XP using the requested formula."""
        streak_bonus = min(streak, 10) * 5
        return base_xp + (correct_guesses * 10) + streak_bonus

    def rank_tier(self, xp: int) -> str:
        """Return rank tier from accumulated XP."""
        if xp >= 5000:
            return "Diamond"
        if xp >= 2500:
            return "Gold"
        if xp >= 1000:
            return "Silver"
        return "Bronze"

    def mvp(self, stats: list[PlayerStats]) -> PlayerStats | None:
        """Choose MVP by most correct guesses and fewest wrong guesses."""
        if not stats:
            return None
        return sorted(stats, key=lambda row: (row.correct_guesses, -row.wrong_guesses), reverse=True)[0]

    async def apply_match_results(
        self,
        game_id: UUID,
        winner_team: Team,
        stats: list[PlayerStats],
        users: UserRepository,
        history: MatchHistoryRepository,
    ) -> None:
        """Update user XP/win counts and create match-history rows atomically within caller transaction."""
        for row in stats:
            user = await users.get(row.user_id)
            if user is None:
                continue
            is_winner = row.team == winner_team
            xp = self.calculate_xp(row.correct_guesses, row.streak)
            user.xp += xp
            user.level = max(1, user.xp // 500 + 1)
            user.streak = row.streak + 1 if is_winner else 0
            if is_winner:
                user.win_count += 1
            else:
                user.lose_count += 1
            await history.create(
                game_id=game_id,
                user_id=row.user_id,
                team=row.team,
                role=row.role,
                is_winner=is_winner,
                xp_earned=xp,
                clues_given=row.clues_given,
                correct_guesses=row.correct_guesses,
            )
