# services/queue_service.py
from celery import Celery
from config import config

celery_app = Celery(
    "delta_os",
    broker=config.get("redis.url", "redis://localhost:6379/0"),
    backend=config.get("redis.url", "redis://localhost:6379/0"),
)


@celery_app.task
def process_ethical_evaluation(plan_data):
    # Async ethical evaluation
    return evaluate_ethical_impact(plan_data)


def evaluate_ethical_impact(plan_data):
    """Evaluate supplied principle scores before handing a plan downstream.

    The task accepts a mapping containing a non-empty ``principles`` mapping
    with numeric scores in the inclusive 0..1 range.  Invalid work is rejected
    explicitly instead of failing later with an undefined function error.
    """
    if not isinstance(plan_data, dict):
        raise ValueError("plan_data must be a mapping")
    principles = plan_data.get("principles")
    if not isinstance(principles, dict) or not principles:
        raise ValueError("plan_data.principles must be a non-empty mapping")

    try:
        scores = [float(score) for score in principles.values()]
    except (TypeError, ValueError) as exc:
        raise ValueError("principle scores must be numeric") from exc
    if any(score < 0 or score > 1 for score in scores):
        raise ValueError("principle scores must be between 0 and 1")

    overall_score = sum(scores) / len(scores)
    return {
        "overall_score": overall_score,
        "is_approved": overall_score >= 0.8,
        "principles_evaluated": len(scores),
    }
