# backend/app/workers/tasks/rewards.py
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def grant_daily_login_reward(self: object, user_id: str) -> dict[str, str]:
    """Grant a daily login reward safely to retry."""
    # TODO: Store reward idempotency keys in Redis or achievements.
    logger.info("daily_login_reward_queued", extra={"user_id": user_id})
    return {"status": "queued", "user_id": user_id}


@celery_app.task(bind=True)
def process_seasonal_event_rewards(self: object) -> dict[str, str]:
    """Process seasonal event rewards."""
    logger.info("seasonal_event_rewards_tick")
    return {"status": "ok"}
