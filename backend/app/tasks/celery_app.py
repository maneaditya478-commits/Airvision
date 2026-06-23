from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "airvision",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    beat_schedule={
        "detect-hcho-hotspots": {
            "task": "app.tasks.tasks.detect_hotspots_task",
            "schedule": crontab(minute=0, hour="*/6"),
        },
        "refresh-aqi-predictions": {
            "task": "app.tasks.tasks.refresh_predictions_task",
            "schedule": crontab(minute=30, hour="*/3"),
        },
    },
)

celery_app.autodiscover_tasks(["app.tasks"])
