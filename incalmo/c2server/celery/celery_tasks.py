from incalmo.incalmo_runner import run_incalmo_strategy
from config.attacker_config import AttackerConfig
import asyncio
from datetime import datetime, timedelta

from incalmo.c2server.celery.celery_worker import celery_worker
from incalmo.c2server.shared import (
    TaskState,
    agents,
    agent_deletion_queue,
    command_queues,
    AGENT_TIMEOUT_SECONDS,
)
from celery import Celery


@celery_worker.task(bind=True, name="run_incalmo_strategy_task")
def run_incalmo_strategy_task(self, config_dict: dict):
    config = AttackerConfig(**config_dict)
    if not config.id:
        raise Exception("No task ID specified")

    # Run the strategy
    task_id = config.id
    asyncio.run(run_incalmo_strategy(config, task_id))

    return {"status": str(TaskState.SUCCESS)}


@celery_worker.task(bind=True, name="cancel_strategy_task")
def cancel_strategy_task(self, task_id: str):
    """Cancel a running strategy task."""
    celery_worker.control.revoke(task_id, terminate=True, signal="SIGTERM")
    return {"status": str(TaskState.SUCCESS), "message": f"Task {task_id} cancelled"}


# Note: Periodic tasks are now configured directly in celery_worker.py
# using beat_schedule configuration instead of signals


@celery_worker.task(bind=True, name="cleanup_stale_agents")
def cleanup_stale_agents(self):
    """Remove agents that haven't beaconed within the timeout period."""
    print(f"[INFO] Checking for stale agents")
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(seconds=AGENT_TIMEOUT_SECONDS)

    stale_agents = []

    # Find agents that haven't beaconed recently
    for paw, agent_data in list(agents.items()):
        last_beacon = agent_data.get("last_beacon")

        # Handle agents without last_beacon timestamp (legacy agents)
        if last_beacon is None:
            print(f"[WARNING] Agent {paw} has no last_beacon timestamp, assuming stale")
            stale_agents.append(paw)
        elif last_beacon < cutoff_time:
            print(f"[INFO] Agent {paw} is stale (last beacon: {last_beacon})")
            stale_agents.append(paw)

    # Remove stale agents
    for paw in stale_agents:
        print(f"[INFO] Cleaning up stale agent: {paw}")
        # Remove from main agents dict
        if paw in agents:
            del agents[paw]
        # Remove command queue
        if paw in command_queues:
            del command_queues[paw]
        # Remove from deletion queue if present
        if paw in agent_deletion_queue:
            agent_deletion_queue.remove(paw)

    return {
        "status": str(TaskState.SUCCESS),
        "cleaned_agents": stale_agents,
        "count": len(stale_agents),
        "message": f"Cleaned up {len(stale_agents)} stale agents",
    }
