from celery import current_task
from incalmo.incalmo_runner import run_incalmo_strategy
import asyncio
import traceback
import os

# Import the worker's celery instance
from incalmo.c2server.celery.celery_worker import celery_worker


@celery_worker.task(bind=True, name="run_incalmo_strategy_task")
def run_incalmo_strategy_task(self, strategy_name: str):
    """
    Celery task to run an Incalmo strategy.
    """
    try:
        print(f"[CELERY_TASK] Starting strategy: {strategy_name}")
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": f"Starting {strategy_name}..."},
        )

        # Run the strategy
        result = asyncio.run(run_incalmo_strategy(strategy_name))

        self.update_state(
            state="PROGRESS",
            meta={"current": 100, "total": 100, "status": "Strategy completed"},
        )

        print(f"[CELERY_TASK] Strategy {strategy_name} completed successfully")
        return {"status": "success", "result": result, "strategy": strategy_name}

    except Exception as e:
        print(f"[CELERY_TASK] Strategy {strategy_name} failed: {str(e)}")
        traceback.print_exc()
        self.update_state(
            state="FAILURE", meta={"error": str(e), "traceback": traceback.format_exc()}
        )
        raise


@celery_worker.task(bind=True, name="cancel_strategy_task")
def cancel_strategy_task(self, task_id: str):
    """Cancel a running strategy task."""
    try:
        celery_worker.control.revoke(task_id, terminate=True)
        return {"status": "success", "message": f"Task {task_id} cancelled"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to cancel task: {str(e)}"}
