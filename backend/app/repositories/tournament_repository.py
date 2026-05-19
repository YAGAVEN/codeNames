# backend/app/repositories/tournament_repository.py
from app.db.models.tournament import Tournament
from app.repositories.base import BaseRepository


class TournamentRepository(BaseRepository[Tournament]):
    """Database operations for tournaments."""

    model = Tournament
