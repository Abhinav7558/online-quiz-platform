from celery import Celery

from .config import settings

if settings.running_in_docker == False:
    redis_url = "redis://localhost:6379/0"
else:
    redis_url = "redis://redis:6379/0"
celery_app = Celery(
    "quiz_tasks",
    broker=redis_url,
    backend=redis_url,
)

from .tasks import calculate_score
