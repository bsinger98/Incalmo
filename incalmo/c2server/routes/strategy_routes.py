"""
Strategy-related routes for the C2 server.
Handles strategy execution, monitoring, and management.
"""

import json
from flask import Blueprint, request, jsonify, current_app

from config.attacker_config import AttackerConfig
from incalmo.core.strategies.incalmo_strategy import IncalmoStrategy
from incalmo.core.strategies.llm.langchain_registry import LangChainRegistry
from incalmo.c2server.celery.celery_tasks import run_incalmo_strategy_task
from incalmo.c2server.celery.celery_worker import celery_worker
from incalmo.c2server.shared import (
    running_strategy_tasks,
    TaskState,
)
from incalmo.c2server.state_store import StateStore

# Create blueprint
strategy_bp = Blueprint("strategy", __name__)


@strategy_bp.route("/startup", methods=["POST"])
def incalmo_startup():
    """Start an Incalmo strategy as a background task."""
    data = request.get_data()
    json_data = json.loads(data)
    # Clear existing environment hosts when starting a new strategy
    StateStore.set_hosts([])

    # Validate using AttackerConfig schema
    config = AttackerConfig(**json_data)

    strategy_name = config.strategy.planning_llm
    print(f"[FLASK] Starting Celery task for strategy: {strategy_name}")
    print(f"[FLASK] Configuration: {config.model_dump()}")

    # Use the imported task function
    task = run_incalmo_strategy_task.delay(config.model_dump())
    task_id = task.id

    # Cancel any existing strategy with the same name
    if strategy_name in running_strategy_tasks:
        old_task_id = running_strategy_tasks[strategy_name]
        print(f"[FLASK] Cancelling existing task: {old_task_id}")
        current_app.extensions["celery"].control.revoke(old_task_id, terminate=True)

    # Store the task ID
    running_strategy_tasks[strategy_name] = task_id

    response = {
        "status": "success",
        "message": f"Incalmo strategy {strategy_name} started as background task",
        "config": config.model_dump(),
        "task_id": task_id,
        "strategy": strategy_name,
    }

    print(f"[FLASK] Strategy {strategy_name} queued with task ID: {task_id}")
    return jsonify(response), 202  # 202 Accepted for async operation


@strategy_bp.route("/strategy_status/<strategy_name>", methods=["GET"])
def strategy_status(strategy_name):
    """Check the status of a running strategy."""
    if strategy_name not in running_strategy_tasks:
        return jsonify({"error": "Strategy not found"}), 404

    task_id = running_strategy_tasks[strategy_name]
    task = run_incalmo_strategy_task.AsyncResult(task_id)
    task_state = TaskState.from_string(task.state)

    # Safely handle task.info
    task_info = {}
    if task.info:
        try:
            if isinstance(task.info, dict):
                task_info = task.info
            elif isinstance(task.info, Exception):
                task_info = {"error": str(task.info), "type": type(task.info).__name__}
            else:
                task_info = {"info": str(task.info)}
        except Exception as e:
            task_info = {"serialization_error": str(e)}

    response = {
        "strategy": strategy_name,
        "task_id": task_id,
        "state": str(task_state),
        "info": task_info,
    }

    if task_state == TaskState.PENDING:
        response["status"] = "Task is waiting to be processed"
    elif task_state == TaskState.PROGRESS:
        response["status"] = task_info.get("status", "In progress")
        response["current"] = task_info.get("current", 0)
        response["total"] = task_info.get("total", 100)
    elif task_state == TaskState.SUCCESS:
        response["status"] = "Task completed successfully"
        response["result"] = task_info
    elif task_state == TaskState.FAILURE:
        response["status"] = "Task failed"
        response["error"] = task_info.get("error", str(task.info))

    return jsonify(response), 200


@strategy_bp.route("/task_status/<task_id>", methods=["GET"])
def task_status(task_id):
    """Check the status of a task by its ID."""
    task = run_incalmo_strategy_task.AsyncResult(task_id)
    task_state = TaskState.from_string(task.state)

    # Safely handle task.info
    task_info = {}
    if task.info:
        try:
            if isinstance(task.info, dict):
                task_info = task.info
            elif isinstance(task.info, Exception):
                task_info = {"error": str(task.info), "type": type(task.info).__name__}
            else:
                task_info = {"info": str(task.info)}
        except Exception as e:
            task_info = {"serialization_error": str(e)}

    response = {"task_id": task_id, "state": str(task_state), "info": task_info}

    if task_state == TaskState.PENDING:
        response["status"] = "Task is waiting to be processed"
    elif task_state == TaskState.PROGRESS:
        response["status"] = task_info.get("status", "In progress")
    elif task_state == TaskState.SUCCESS:
        response["status"] = "Task completed successfully"
        response["result"] = task_info
    elif task_state == TaskState.FAILURE:
        response["status"] = "Task failed"
        response["error"] = task_info.get("error", str(task.info))

    return jsonify(response), 200


@strategy_bp.route("/cancel_strategy/<strategy_name>", methods=["POST"])
def cancel_strategy(strategy_name):
    """Cancel a running strategy."""
    if strategy_name not in running_strategy_tasks:
        return jsonify({"error": "Strategy not found"}), 404

    task_id = running_strategy_tasks[strategy_name]
    # Revoke the task with terminate=True and signal='SIGKILL'
    celery_worker.control.revoke(task_id, terminate=True, signal="SIGTERM")

    # Remove from tracking immediately
    del running_strategy_tasks[strategy_name]

    print(f"[FLASK] Strategy {strategy_name} cancelled and removed from tracking")

    return jsonify(
        {
            "message": f"Strategy {strategy_name} cancelled successfully",
            "task_id": task_id,
            "status": str(TaskState.REVOKED),
        }
    ), 200


@strategy_bp.route("/running_strategies", methods=["GET"])
def list_strategies():
    """List all currently running strategies."""
    strategies = {}
    completed_strategies = []

    for strategy_name, task_id in running_strategy_tasks.items():
        task = run_incalmo_strategy_task.AsyncResult(task_id)

        task_state = TaskState.from_string(task.state)
        task_info = {}
        if task_state == TaskState.PENDING:
            task_info = {
                "status": "waiting",
                "message": "Task is waiting to be processed",
            }
        elif task_state == TaskState.STARTED:
            task_info = {"status": "running", "message": "Task is currently running"}
        elif task_state == TaskState.SUCCESS:
            task_info = {
                "status": "completed",
                "message": "Task completed successfully",
            }
            try:
                if hasattr(task, "result") and task.result:
                    task_info["result"] = str(task.result)
            except Exception:
                pass  # Ignore result access errors
        elif task_state == TaskState.FAILURE:
            task_info = {"status": "failed", "message": "Task failed"}
            try:
                if hasattr(task, "result") and task.result:
                    task_info["error"] = str(task.result)
            except Exception:
                task_info["error"] = "Unknown error occurred"
        elif task_state == TaskState.REVOKED:
            task_info = {"status": "cancelled", "message": "Task was cancelled"}
        else:
            task_info = {
                "status": str(task_state),
                "message": f"Task is in {task_state} state",
            }

        strategies[strategy_name] = {
            "task_id": task_id,
            "state": task.state,
            "info": task_info,
        }

        # Mark completed/failed/revoked strategies for cleanup
        if task.state in [TaskState.SUCCESS, TaskState.FAILURE, TaskState.REVOKED]:
            completed_strategies.append(strategy_name)

    # Clean up completed strategies
    for strategy_name in completed_strategies:
        print(f"[FLASK] Cleaning up completed strategy: {strategy_name}")
        del running_strategy_tasks[strategy_name]

    return jsonify(strategies), 200


@strategy_bp.route("/available_strategies", methods=["GET"])
def get_available_strategies():
    """Get all available strategies from the registry."""
    strategies = []
    for strategy_name, strategy_class in IncalmoStrategy._registry.items():
        if strategy_name not in ["langchain", "llmstrategy"]:
            strategies.append(
                {
                    "name": strategy_name,
                }
            )
        elif strategy_name == "langchain":
            models = LangChainRegistry().list_models()
            for model in models:
                strategies.append(
                    {
                        "name": model,
                    }
                )

    strategies.sort(key=lambda x: x["name"])
    return jsonify({"strategies": strategies}), 200
