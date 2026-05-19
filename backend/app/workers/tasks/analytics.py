# backend/app/workers/tasks/analytics.py
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def aggregate_daily_stats(self: object) -> dict[str, str]:
    """Aggregate daily analytics at midnight UTC."""
    # TODO: Persist aggregate snapshots to Supabase/Postgres analytics tables.
    logger.info("aggregate_daily_stats_tick")
    return {"status": "ok"}


@celery_app.task(bind=True)
def compute_leaderboard_snapshot(self: object) -> dict[str, str]:
    """Compute cached leaderboard snapshot every 15 minutes."""
    # TODO: Write leaderboard snapshot to Redis for ultra-fast reads.
    logger.info("leaderboard_snapshot_tick")
    return {"status": "ok"}
