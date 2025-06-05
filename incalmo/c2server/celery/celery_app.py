from celery import Celery
from flask import Flask
import os


def make_celery(app: Flask):
    # Configure Celery
    broker = app.config.get("broker_url") or os.environ.get(
        "broker_url", "redis://localhost:6379/0"
    )
    backend = app.config.get("result_backend") or os.environ.get(
        "result_backend", "redis://localhost:6379/0"
    )

    print(f"[CELERY_APP] Using broker: {broker}")
    print(f"[CELERY_APP] Using backend: {backend}")

    # Configure Celery with explicit Redis transport
    celery = Celery(
        app.import_name,
        broker=broker,
        backend=backend,
    )

    # Additional Celery configuration
    celery.conf.update(
        broker_url=broker,
        result_backend=backend,
        broker_transport="redis",  # Force Redis transport
        broker_connection_retry_on_startup=True,  # Retry connection on startup
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,
        task_soft_time_limit=25 * 60,
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
    )

    # Ensure tasks run with Flask app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery
