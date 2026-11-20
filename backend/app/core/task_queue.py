from celery import Celery
from app.config import settings

celery_app = Celery(
    "seo_bot",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.audit_tasks",
        "app.tasks.keyword_tasks",
        "app.tasks.report_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Karachi",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_soft_time_limit=600,   # 10 min per task
    task_time_limit=660,
    worker_prefetch_multiplier=1,
)
