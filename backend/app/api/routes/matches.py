# backend/app/api/routes/matches.py
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth_deps import get_current_user
from app.api.dependencies.db_deps import get_db
from app.api.dependencies.rate_limit import user_route_rate_limit
from app.db.models.user import User
from app.schemas.common import EnvelopeSchema
from app.schemas.matches import MatchHistoryRead, MatchRead, ReplayRead
from app.services.match_service import MatchService
from app.utils.responses import success_response

router = APIRouter()


@router.get("/history", response_model=EnvelopeSchema[list[MatchHistoryRead]], summary="Match history")
async def history(
    page: int = 1,
    per_page: int = 20,
    _rate_limit: None = Depends(user_route_rate_limit),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return current user's match history."""
    rows = await MatchService(db).history_for_user(user.id, page, per_page)
    return success_response(rows, {"page": page, "per_page": per_page})


@router.get("/{game_id}", response_model=EnvelopeSchema[MatchRead], summary="Match details")
async def match_details(game_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    """Return a game summary."""
    return success_response(await MatchService(db).get_match(game_id))


@router.get("/{game_id}/replay", response_model=EnvelopeSchema[ReplayRead], summary="Match replay")
async def replay(game_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    """Return structured replay data."""
    return success_response(await MatchService(db).replay(game_id))
