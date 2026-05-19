# backend/app/api/routes/admin.py
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth_deps import require_admin
from app.api.dependencies.db_deps import get_db
from app.db.models.user import User
from app.schemas.admin import AnalyticsRead, ReportRead, ResolveReportRequest
from app.schemas.common import EnvelopeSchema, MessageResponse
from app.schemas.users import UserRead
from app.services.admin_service import AdminService
from app.utils.responses import success_response

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("/users", response_model=EnvelopeSchema[list[UserRead]], summary="Admin list users")
async def users(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)) -> dict:
    """List users for moderation."""
    return success_response(await AdminService(db).list_users(limit, offset))


@router.post("/ban/{user_id}", response_model=EnvelopeSchema[UserRead], summary="Ban user")
async def ban_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    """Ban a user."""
    return success_response(await AdminService(db).ban_user(user_id))


@router.delete("/rooms/{room_id}", response_model=EnvelopeSchema[MessageResponse], summary="Admin delete room")
async def delete_room(room_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    """Delete any room as admin."""
    await AdminService(db).delete_room(room_id)
    return success_response(MessageResponse(message="Room deleted"))


@router.get("/reports", response_model=EnvelopeSchema[list[ReportRead]], summary="Open reports")
async def reports(db: AsyncSession = Depends(get_db)) -> dict:
    """List open reports."""
    return success_response(await AdminService(db).list_reports())


@router.post("/reports/{id}/resolve", response_model=EnvelopeSchema[ReportRead], summary="Resolve report")
async def resolve_report(id: UUID, payload: ResolveReportRequest, db: AsyncSession = Depends(get_db)) -> dict:
    """Resolve or dismiss a report."""
    return success_response(await AdminService(db).resolve_report(id, payload.status))


@router.get("/analytics", response_model=EnvelopeSchema[AnalyticsRead], summary="Admin analytics")
async def analytics(db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)) -> dict:
    """Return operational analytics."""
    return success_response(await AdminService(db).analytics())
