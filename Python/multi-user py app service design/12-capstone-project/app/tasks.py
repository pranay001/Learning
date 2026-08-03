import time
from celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def generate_order_report(self, username: str):
    """
    Simulates a slow report-generation job (e.g. aggregating a user's order
    history into a PDF). Runs on a Celery worker, completely decoupled from
    the API process — the API returns a task_id immediately (see main.py).
    """
    try:
        time.sleep(8)  # simulate heavy aggregation/rendering work
        return {
            "username": username,
            "status": "complete",
            "orders_included": 0,  # placeholder — a real version would query the DB
            "generated_at": time.time(),
        }
    except Exception as exc:
        raise self.retry(exc=exc)
