"""
Logging-related routes for the C2 server.
Handles streaming of various log files.
"""

import json
import time
from flask import Blueprint, Response, stream_with_context

from incalmo.c2server.shared import (
    running_strategy_tasks,
    get_latest_log_path,
)

# Create blueprint
logging_bp = Blueprint("logging", __name__)


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
    position = 0
    last_check_time = 0

    while True:
        # Check for a newer log file every 10 seconds
        current_time = time.time()
        if current_time - last_check_time > 10 or current_log_path is None:
            if not running_strategy_tasks:
                time.sleep(2)
                continue
            try:
                strategy_name = next(iter(running_strategy_tasks.keys()))
                task_id = running_strategy_tasks[strategy_name]
                latest_log_path = get_latest_log_path(strategy_name, task_id)[log_index]
                log_names = ["Action", "LLM", "LLM Agent"]
                print(
                    f"[DEBUG] Latest {log_names[log_index]} log path: {latest_log_path}"
                )
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
            with open(current_log_path, "r") as f:
                f.seek(position)
                for line in f:
                    yield f"data: {line.strip()}\n\n"
                position = f.tell()
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
