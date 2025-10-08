from celery import Celery

celery_app = Celery(
    "quiz_tasks",
    broker_url="redis://localhost:6379/0",
    result_backend="redis://localhost:6379/0",
)

from .tasks import calculate_score
