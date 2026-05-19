# backend/app/services/admin_service.py
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.game_repository import GameRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin import AnalyticsRead
from app.utils.constants import OnlineStatus, ReportStatus, RoomStatus
from app.utils.exceptions import NotFoundError


class AdminService:
    """Moderator and admin-only operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)
        self.rooms = RoomRepository(session)
        self.reports = ReportRepository(session)
        self.games = GameRepository(session)

    async def list_users(self, limit: int = 100, offset: int = 0) -> list[object]:
        """List users for admin tools."""
        return await self.users.list(limit=limit, offset=offset)

    async def ban_user(self, user_id: UUID) -> object:
        """Mark a user banned without changing their immutable auth identity."""
        user = await self.users.get(user_id)
        if user is None:
            raise NotFoundError("User not found")
        user.online_status = OnlineStatus.BANNED
        await self.users.commit()
        return user

    async def delete_room(self, room_id: UUID) -> None:
        """Admin-delete a room."""
        room = await self.rooms.get(room_id)
        if room is None:
            raise NotFoundError("Room not found")
        await self.rooms.delete(room)
        await self.rooms.commit()

    async def list_reports(self) -> list[object]:
        """List open reports."""
        return await self.reports.list_open()

    async def resolve_report(self, report_id: UUID, status: ReportStatus) -> object:
        """Resolve or dismiss a report."""
        report = await self.reports.get(report_id)
        if report is None:
            raise NotFoundError("Report not found")
        updated = await self.reports.set_status(report, status)
        await self.reports.commit()
        return updated

    async def analytics(self) -> AnalyticsRead:
        """Return basic operational analytics."""
        return AnalyticsRead(
            users=await self.users.count(),
            rooms=await self.rooms.count(),
            active_rooms=await self.rooms.count(RoomStatus.IN_PROGRESS),
            games=await self.games.count(),
            reports_open=await self.reports.count_open(),
        )
