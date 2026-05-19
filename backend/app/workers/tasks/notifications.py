# backend/app/workers/tasks/notifications.py
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, autoretry_for=(TimeoutError,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def push_notification(self: object, user_id: str, payload: dict) -> dict[str, object]:
    """Push a user notification idempotently."""
    # TODO: Fan out through Supabase Realtime or mobile push provider.
    logger.info("notification_push_queued", extra={"user_id": user_id})
    return {"status": "queued", "user_id": user_id, "payload": payload}


@celery_app.task(bind=True, autoretry_for=(TimeoutError,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def broadcast_achievement_unlock(self: object, user_id: str, badge_key: str) -> dict[str, str]:
    """Broadcast achievement unlock idempotently."""
    logger.info("achievement_broadcast_queued", extra={"user_id": user_id, "badge_key": badge_key})
    return {"status": "queued", "user_id": user_id, "badge_key": badge_key}
