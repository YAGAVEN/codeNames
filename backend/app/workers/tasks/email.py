# backend/app/workers/tasks/email.py
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, autoretry_for=(TimeoutError,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_verification_email(self: object, user_id: str) -> dict[str, str]:
    """Send verification email idempotently for a user."""
    # TODO: Integrate transactional email provider or Supabase email hooks.
    logger.info("verification_email_queued", extra={"user_id": user_id})
    return {"status": "queued", "user_id": user_id}


@celery_app.task(bind=True, autoretry_for=(TimeoutError,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_password_reset_email(self: object, user_id: str, token: str) -> dict[str, str]:
    """Send password reset email idempotently for a token."""
    # TODO: Build reset URL from frontend origin and send through email provider.
    logger.info("password_reset_email_queued", extra={"user_id": user_id})
    return {"status": "queued", "user_id": user_id, "token_tail": token[-8:]}


@celery_app.task(bind=True, autoretry_for=(TimeoutError,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_friend_request_email(self: object, from_id: str, to_id: str) -> dict[str, str]:
    """Notify a player about a friend request."""
    logger.info("friend_request_email_queued", extra={"from_id": from_id, "to_id": to_id})
    return {"status": "queued", "from_id": from_id, "to_id": to_id}
