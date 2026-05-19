# backend/app/workers/tasks/cleanup.py
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def purge_abandoned_rooms(self: object) -> dict[str, str]:
    """Purge abandoned waiting rooms on a schedule."""
    # TODO: Query rooms with no active Redis presence and delete/archive them.
    logger.info("purge_abandoned_rooms_tick")
    return {"status": "ok"}


@celery_app.task(bind=True)
def expire_stale_tokens(self: object) -> dict[str, str]:
    """Expire stale token records beyond Redis TTL guarantees."""
    logger.info("expire_stale_tokens_tick")
    return {"status": "ok"}


@celery_app.task(bind=True)
def archive_old_match_history(self: object) -> dict[str, str]:
    """Archive old match history rows to cold storage."""
    # TODO: Export historical rows to Supabase Storage before deletion.
    logger.info("archive_old_match_history_tick")
    return {"status": "ok"}
