# backend/app/schemas/admin.py
from datetime import datetime
from uuid import UUID

from app.schemas.common import StrictSchema
from app.utils.constants import ReportStatus


class ReportRead(StrictSchema):
    """Moderation report response."""

    id: UUID
    reporter_id: UUID
    reported_id: UUID
    reason: str
    status: ReportStatus
    created_at: datetime


class AnalyticsRead(StrictSchema):
    """Operational analytics snapshot."""

    users: int
    rooms: int
    active_rooms: int
    games: int
    reports_open: int


class ResolveReportRequest(StrictSchema):
    """Resolve or dismiss a report."""

    status: ReportStatus = ReportStatus.RESOLVED
