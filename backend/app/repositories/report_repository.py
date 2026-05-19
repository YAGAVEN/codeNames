# backend/app/repositories/report_repository.py
from uuid import UUID

from sqlalchemy import func, select

from app.db.models.report import Report
from app.repositories.base import BaseRepository
from app.utils.constants import ReportStatus


class ReportRepository(BaseRepository[Report]):
    """Database operations for moderation reports."""

    model = Report

    async def create(self, reporter_id: UUID, reported_id: UUID, reason: str) -> Report:
        """Create a report."""
        report = Report(reporter_id=reporter_id, reported_id=reported_id, reason=reason)
        return await self.add(report)

    async def list_open(self, limit: int = 100) -> list[Report]:
        """List open moderation reports."""
        result = await self.session.execute(select(Report).where(Report.status == ReportStatus.OPEN).limit(limit))
        return list(result.scalars().all())

    async def set_status(self, report: Report, status: ReportStatus) -> Report:
        """Resolve or dismiss a report."""
        report.status = status
        await self.session.flush()
        return report

    async def count_open(self) -> int:
        """Count open reports."""
        result = await self.session.execute(select(func.count()).select_from(Report).where(Report.status == ReportStatus.OPEN))
        return int(result.scalar_one())
