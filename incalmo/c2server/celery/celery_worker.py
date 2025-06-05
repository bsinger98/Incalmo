#!/usr/bin/env python3
"""
Standalone Celery worker app for running tasks.
This is separate from the Flask app to avoid conflicts.
"""

from celery import Celery
import os

# Configure Celery for worker
broker = os.environ.get("broker_url", "redis://localhost:6379/0")
backend = os.environ.get("result_backend", "redis://localhost:6379/0")

print(f"[CELERY_WORKER] Using broker: {broker}")
print(f"[CELERY_WORKER] Using backend: {backend}")

# Create standalone Celery app for worker
celery_worker = Celery(
    "incalmo_worker",
    broker=broker,
    backend=backend,
    include=["incalmo.c2server.celery.celery_tasks"],
)

# Configure Celery
celery_worker.conf.update(
    broker_url=broker,
    result_backend=backend,
    broker_transport="redis",
    broker_connection_retry_on_startup=True,
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

if __name__ == "__main__":
    celery_worker.start()
