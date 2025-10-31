# services/queue_service.py
from celery import Celery
from config import config

celery_app = Celery(
    'delta_os',
    broker=config.get('redis.url', 'redis://localhost:6379/0'),
    backend=config.get('redis.url', 'redis://localhost:6379/0')
)

@celery_app.task
def process_ethical_evaluation(plan_data):
    # Async ethical evaluation
    return evaluate_ethical_impact(plan_data)
