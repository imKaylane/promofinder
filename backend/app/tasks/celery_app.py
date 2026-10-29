"""Celery application factory."""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "techdeals",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    # Beat schedule — run price check every 30 minutes.
    beat_schedule={
        "check-price-alerts": {
            "task": "app.tasks.tasks.check_price_alerts",
            "schedule": 1800,  # seconds
        },
        "refresh-deals-cache": {
            "task": "app.tasks.tasks.refresh_deals_cache",
            "schedule": 3600,
        },
    },
)
