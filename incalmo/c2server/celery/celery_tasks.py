from incalmo.incalmo_runner import run_incalmo_strategy
from config.attacker_config import AttackerConfig
import asyncio
import traceback
import os

from incalmo.c2server.celery.celery_worker import celery_worker


@celery_worker.task(bind=True, name="run_incalmo_strategy_task")
def run_incalmo_strategy_task(self, config_dict: dict):
    config = AttackerConfig(**config_dict)
    if not config.id:
        raise Exception("No task ID specified")

    try:
        planning_llm = config.strategy.planning_llm
        task_id = config.id
        self.update_state(
            state="PROGRESS",
            meta={
                "current": 0,
                "total": 100,
                "status": f"Starting {planning_llm}...",
                "pid": os.getpid(),
            },
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 25,
                "total": 100,
                "status": f"Executing {planning_llm}...",
                "pid": os.getpid(),
            },
        )

        # Run the strategy
        result = asyncio.run(run_incalmo_strategy(config, task_id))

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 100,
                "total": 100,
                "status": f"Strategy {planning_llm} completed",
            },
        )

        return {
            "status": "success",
            "result": result,
            "strategy": planning_llm,
        }

    except Exception as e:
        print(f"[CELERY_TASK] Strategy {planning_llm} failed with error: {e}")
        traceback.print_exc()

        error_info = {
            "error": str(e),
            "error_type": type(e).__name__,
            "strategy": planning_llm,
        }

        self.update_state(state="FAILURE", meta=error_info)

        return {
            "status": "failed",
            "error": str(e),
            "strategy": planning_llm,
        }


@celery_worker.task(bind=True, name="cancel_strategy_task")
def cancel_strategy_task(self, task_id: str):
    """Cancel a running strategy task."""
    try:
        celery_worker.control.revoke(task_id, terminate=True, signal="SIGTERM")
        return {"status": "success", "message": f"Task {task_id} cancelled"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to cancel task: {str(e)}"}
