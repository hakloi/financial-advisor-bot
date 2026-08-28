from datetime import timedelta

from celery import Celery
from backend.api.config import settings

celery_app = Celery(
	main="fina",
	broker=settings.redis_settings.redis_url,
	backend=settings.redis_settings.redis_url,
)
celery_app.autodiscover_tasks(packages=["backend.services"])
celery_app.conf.beat_schedule = {
	"sync-moex-market-data": {
		"task": "backend.services.tasks.sync_moex_market_data",
		"schedule": timedelta(hours=settings.market_sync_interval_hours),
	},
}