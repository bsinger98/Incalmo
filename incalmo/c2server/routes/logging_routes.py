"""
Logging-related routes for the C2 server.
Handles streaming of various log files.
"""

import json
import time
from flask import Blueprint, Response, stream_with_context, jsonify

from incalmo.c2server.shared import (
    running_strategy_tasks,
    get_latest_log_path,
    get_log_path,
)

# Create blueprint
logging_bp = Blueprint("logging", __name__)


def _get_latest_running_strategy_task():
    """Return the most recently started active running strategy task, if any."""
    active_states = {"PENDING", "STARTED", "RECEIVED", "PROGRESS"}

    for strategy_id, config in reversed(list(running_strategy_tasks.items())):
        try:
            from incalmo.c2server.celery.celery_tasks import run_incalmo_strategy_task

            task_state = str(run_incalmo_strategy_task.AsyncResult(strategy_id).state)
            if task_state in active_states:
                return strategy_id, config
        except Exception:
            # If Celery state lookup fails, fall back to this entry so streaming continues.
            return strategy_id, config

    return None, None


@logging_bp.route("/get_latest_logs", methods=["GET"])
def get_latest_logs():
    """Get the latest logs for all log files."""
    log_path = get_latest_log_path()

    actions_log_path = log_path[0]
    llm_log_path = log_path[1]
    llm_agent_log_path = log_path[2]

    actions_log = ""
    llm_log = ""
    llm_agent_log = ""

    # If the log file does not exist, return an empty string
    if actions_log_path.exists():
        with open(actions_log_path, "r") as f:
            actions_log = f.read()

    if llm_log_path.exists():
        with open(llm_log_path, "r") as f:
            llm_log = f.read()

    if llm_agent_log_path.exists():
        with open(llm_agent_log_path, "r") as f:
            llm_agent_log = f.read()

    logs = {}
    logs["actions"] = actions_log
    logs["llm"] = llm_log
    logs["llm_agent"] = llm_agent_log
    return jsonify(logs), 200


@logging_bp.route("/get_logs/<strategy_id>", methods=["GET"])
def get_logs(strategy_id: str):
    """Get the logs for a strategy."""
    strategy_log_path = get_log_path(strategy_id)

    actions_log_path = strategy_log_path / "actions.json"
    llm_log_path = strategy_log_path / "llm.log"
    llm_agent_log_path = strategy_log_path / "llm_agent.log"
    actions_log = ""
    llm_log = ""
    llm_agent_log = ""

    if actions_log_path.exists():
        with open(actions_log_path, "r") as f:
            actions_log = f.read()

    if llm_log_path.exists():
        with open(llm_log_path, "r") as f:
            llm_log = f.read()

    if llm_agent_log_path.exists():
        with open(llm_agent_log_path, "r") as f:
            llm_agent_log = f.read()

    logs = {}
    logs["actions"] = actions_log
    logs["llm"] = llm_log
    logs["llm_agent"] = llm_agent_log

    return jsonify(logs), 200


def _generate_log_stream(log_index):
    """
    Generic log stream generator.

    Args:
        log_index: Index of the log file to stream (0=actions, 1=llm, 2=llm_agent)
    """
    # Retry in case of initial connection failure
    yield "retry: 1000\n\n"

    # Track the currently streaming log file
    current_log_path = None
    current_active_task_id = None
    position = 0
    last_check_time = 0

    while True:
        # Check for a newer log file every 10 seconds
        current_time = time.time()
        if current_time - last_check_time > 10 or current_log_path is None:
            try:
                task_id, config = _get_latest_running_strategy_task()
                if task_id and config:
                    if task_id != current_active_task_id:
                        current_active_task_id = task_id
                        current_log_path = None
                        position = 0
                        yield f"data: {json.dumps({'status': 'Switched to new log file'})}\n\n"

                    try:
                        latest_log_path = get_latest_log_path(config.name, task_id)[log_index]
                    except FileNotFoundError:
                        current_log_path = None
                        position = 0
                        last_check_time = current_time
                        yield f"data: {json.dumps({'status': 'No log file available yet'})}\n\n"
                        time.sleep(1)
                        continue
                else:
                    current_active_task_id = None
                    latest_log_path = get_latest_log_path()[log_index]

                if latest_log_path != current_log_path:
                    current_log_path = latest_log_path
                    position = 0  # Reset position for the new file
                    yield f"data: {json.dumps({'status': 'Switched to new log file'})}\n\n"
                last_check_time = current_time
            except FileNotFoundError as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                time.sleep(1)
                continue

        # Stream from current log file
        if current_log_path:
            if not current_log_path.exists():
                yield f"data: {json.dumps({'status': 'No log file available yet'})}\n\n"
                time.sleep(1)
                continue

            try:
                with open(current_log_path, "r") as f:
                    f.seek(position)
                    for line in f:
                        yield f"data: {line.strip()}\n\n"
                    position = f.tell()
            except OSError as e:
                # Keep the stream alive even if the file is briefly unavailable.
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        else:
            yield f"data: {json.dumps({'status': 'No log file available yet'})}\n\n"

        time.sleep(1)


@logging_bp.route("/stream_action_logs", methods=["GET"])
def stream_action_logs():
    """Stream action logs via Server-Sent Events."""
    # Set appropriate headers for SSE
    return Response(
        stream_with_context(_generate_log_stream(0)),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


@logging_bp.route("/stream_llm_logs", methods=["GET"])
def stream_llm_logs():
    """Stream LLM logs via Server-Sent Events."""
    # Set appropriate headers for SSE
    return Response(
        stream_with_context(_generate_log_stream(1)),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


@logging_bp.route("/stream_llm_agent_logs", methods=["GET"])
def stream_llm_agent_logs():
    """Stream LLM agent logs via Server-Sent Events."""
    # Set appropriate headers for SSE
    return Response(
        stream_with_context(_generate_log_stream(2)),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )
