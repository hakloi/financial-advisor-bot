from celery import Celery
from backend.api.config import settings

celery_app = Celery(
	main="fina",
	broker=settings.redis_settings.redis_url,
	backend=settings.redis_settings.redis_url,
)
celery_app.autodiscover_tasks(packages=["backend.services"])