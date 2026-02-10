"""Celery application configuration."""

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "threat_modeling",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.analysis.tasks.analysis_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "scan-pending-analyses": {
            "task": "app.analysis.tasks.analysis_tasks.scan_pending_analyses",
            "schedule": crontab(minute="*"),  # Every minute
        },
    },
)
