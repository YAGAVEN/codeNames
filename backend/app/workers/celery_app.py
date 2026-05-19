# backend/app/workers/celery_app.py
from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "codenames_india",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.tasks.email",
        "app.workers.tasks.notifications",
        "app.workers.tasks.cleanup",
        "app.workers.tasks.rewards",
        "app.workers.tasks.analytics",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "purge-abandoned-rooms": {
            "task": "app.workers.tasks.cleanup.purge_abandoned_rooms",
            "schedule": 600.0,
        },
        "expire-stale-tokens": {
            "task": "app.workers.tasks.cleanup.expire_stale_tokens",
            "schedule": 3600.0,
        },
        "archive-old-match-history": {
            "task": "app.workers.tasks.cleanup.archive_old_match_history",
            "schedule": 86400.0,
        },
        "leaderboard-snapshot": {
            "task": "app.workers.tasks.analytics.compute_leaderboard_snapshot",
            "schedule": 900.0,
        },
        "daily-stats": {
            "task": "app.workers.tasks.analytics.aggregate_daily_stats",
            "schedule": 86400.0,
        },
    },
)
