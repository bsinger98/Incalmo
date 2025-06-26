from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    send_file,
    Response,
    stream_with_context,
)
from flask_cors import CORS
import json
import base64
import psutil
import binascii
import asyncio
from enum import Enum
import time
from incalmo.models.instruction import Instruction
import uuid
from collections import defaultdict
from string import Template
import logging
from pathlib import Path
import os
from typing import Dict

from incalmo.c2server.celery.celery_app import make_celery
from incalmo.c2server.celery.celery_tasks import run_incalmo_strategy_task
from incalmo.c2server.celery.celery_worker import celery_worker

from incalmo.core.strategies.incalmo_strategy import IncalmoStrategy
from incalmo.core.strategies.llm.langchain_registry import LangChainRegistry

from incalmo.models.command import Command, CommandStatus
from incalmo.models.command_result import CommandResult
from incalmo.incalmo_runner import run_incalmo_strategy
from config.attacker_config import AttackerConfig

from string import Template
import logging
from pathlib import Path
import os
import debugpy

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure Flask for Celery
app.config.update(
    broker_url=os.environ.get("broker_url", "redis://localhost:6379/0"),
    result_backend=os.environ.get("result_backend", "redis://localhost:6379/0"),
)
celery = make_celery(app)
app.extensions["celery"] = celery

print(f"[DEBUG] Flask app broker_url: {app.config.get('broker_url')}")
print(f"[DEBUG] Flask app result_backend: {app.config.get('result_backend')}")
print(f"[DEBUG] Environment broker_url: {os.environ.get('broker_url')}")
print(f"[DEBUG] Environment result_backend: {os.environ.get('result_backend')}")
print(f"[DEBUG] Celery broker URL: {celery.conf.broker_url}")
print(f"[DEBUG] Celery result backend: {celery.conf.result_backend}")
# Disable Flask's default request logging
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

# Define base directories
BASE_DIR = Path(__file__).parent
PAYLOADS_DIR = BASE_DIR / "payloads"
TEMPLATE_PAYLOADS_DIR = PAYLOADS_DIR / "template_payloads"
AGENTS_DIR = BASE_DIR / "agents"

# Debug configuration
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DEBUG_PORT = int(os.getenv("DEBUG_PORT", 5678))

# Store agents and their pending commands
agents = {}
agent_deletion_queue = set()
command_queues = defaultdict(list)
command_results: dict[str, Command] = {}

# Store environment info
hosts = []

# Store running strategy tasks
running_strategy_tasks: Dict[str, str] = {}  # strategy_name -> task_id


# Enums
class TaskState(Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    REVOKED = "REVOKED"
    RETRY = "RETRY"
    RECEIVED = "RECEIVED"
    PROGRESS = "PROGRESS"

    @classmethod
    def from_string(cls, state_str):
        try:
            if not state_str or not isinstance(state_str, str):
                # If state_str is None or empty, return PENDING
                return cls.PENDING
            return cls(state_str)

        except (ValueError, KeyError, AttributeError, TypeError) as e:
            # Return default state when conversion fails
            return cls.PENDING

    def __str__(self):
        return self.value


def decode_base64(data):
    return base64.b64decode(data).decode("utf-8")


def encode_base64(data):
    return str(base64.b64encode(json.dumps(data).encode()), "utf-8")


def read_template_file(filename):
    template_path = TEMPLATE_PAYLOADS_DIR / filename
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {filename}")
    return Template(template_path.read_text())


def get_latest_log_path():
    # Find the most recent log directory
    output_dirs = sorted(Path("output").glob("*_*-*-*"), reverse=True)
    if not output_dirs:
        raise FileNotFoundError("No log directories found")

    latest_dir = output_dirs[0]
    # Get the actions.json file path
    actions_log_path = latest_dir / "actions.json"

    # Get the llm.log file path
    llm_log_path = latest_dir / "llm.log"

    return actions_log_path, llm_log_path


# Agent check-in
@app.route("/beacon", methods=["POST"])
def beacon():
    data = request.data
    decoded_data = decode_base64(data)
    json_data = json.loads(decoded_data)

    paw = json_data.get("paw")
    results = json_data.get("results", [])

    if not paw:
        paw = str(uuid.uuid4())[:8]

    # Store agent info if new
    required_fields = ["host_ip_addrs"]
    if paw not in agents and paw not in agent_deletion_queue:
        # Validate all required fields are present and not None
        if all(json_data.get(field) not in (None, "", []) for field in required_fields):
            print(f"New agent: {paw}")
            agents[paw] = {"paw": paw, "info": data, "infected_by": None}
        else:
            print(
                f"[ERROR] Agent {paw} missing required fields, not adding: "
                f"{ {field: json_data.get(field) for field in required_fields} }"
            )
            return jsonify({"error": "Agent missing required fields"}), 400

    # Process any results from previous commands
    for result in results:
        command_id = result.get("id")
        if command_id in command_results:
            result = CommandResult(**result)
            result.output = decode_base64(result.output)
            result.stderr = decode_base64(result.stderr)

            command_results[command_id].result = result
            command_results[command_id].status = CommandStatus.COMPLETED
    # Get next command from queue if available
    instructions = []
    if command_queues[paw]:
        next_command = command_queues[paw].pop(0)
        instructions.append(next_command)

    sleep_time = 3
    if paw in agent_deletion_queue:
        del agents[paw]
        del command_queues[paw]
        agent_deletion_queue.remove(paw)
        sleep_time = 10  # Do not beacon for a while to allow for proper deletion

    response = {
        "paw": paw,
        "sleep": sleep_time,
        "watchdog": int(60),
        "instructions": json.dumps([json.dumps(i.display) for i in instructions]),
    }

    encoded_response = encode_base64(response)
    return encoded_response


# Get agents
@app.route("/agents", methods=["GET"])
def get_agents():
    agents_list = {}
    for paw, data in agents.items():
        try:
            decoded_info = decode_base64(data["info"])
            parsed_info = json.loads(decoded_info)

            agents_list[paw] = {
                "paw": paw,
                "username": parsed_info.get("username"),
                "privilege": parsed_info.get("privilege"),
                "pid": parsed_info.get("pid"),
                "host_ip_addrs": parsed_info.get("host_ip_addrs"),
            }
        except (binascii.Error, UnicodeDecodeError) as exc:
            raise ValueError(f"Invalid base64 data: {exc!r}")
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON: {exc!r}")

    return jsonify(agents_list)


# Update hosts
@app.route("/update_environment_state", methods=["POST"])
def update_environment_state():
    global hosts
    try:
        data = request.data
        json_data = json.loads(data)

        hosts = json_data.get("hosts", [])
        return jsonify(
            {"status": "success", "message": "Infection source reported"}
        ), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 400


# Get hosts
@app.route("/hosts", methods=["GET"])
def get_hosts():
    return jsonify(
        {
            "hosts": hosts,
        }
    ), 200


@app.route("/agent/delete/<paw>", methods=["DELETE"])
def delete_agent(paw):
    if paw not in agents:
        return jsonify({"error": "Agent not found"}), 404

    # Queue a kill command for the agent
    decoded_info = decode_base64(agents[paw]["info"])
    agent_info = json.loads(decoded_info)
    agent_pid = agent_info.get("pid")

    kill_command = f"(sleep 3 && kill -9 {agent_pid}) &"
    exec_template = read_template_file("Exec_Bash_Template.sh")
    executor_script_content = exec_template.safe_substitute(command=kill_command)
    executor_script_path = PAYLOADS_DIR / "kill_agent.sh"
    executor_script_path.write_text(executor_script_content)

    command_id = str(uuid.uuid4())
    instruction = Instruction(
        id=command_id,
        command=encode_base64("./kill_agent.sh"),
        executor="sh",
        timeout=60,
        payloads=["kill_agent.sh"],
        uploads=[],
        delete_payload=True,
    )

    # Add command to queue
    command_queues[paw].append(instruction)
    command_results[command_id] = Command(
        id=command_id,
        instructions=instruction,
        status=CommandStatus.PENDING,
        result=None,
    )

    agent_deletion_queue.add(paw)

    return jsonify({"message": f"Agent {paw} deleted successfully"}), 200


# Send command to a specific agent
@app.route("/send_command", methods=["POST"])
def send_command():
    try:
        data = request.data
        json_data = json.loads(data)
        agent = json_data.get("agent")
        command = json_data.get("command")
        payloads = json_data.get("payloads", [])

        if not agent or not command:
            return jsonify({"error": "Missing agent or command"}), 400

        if agent not in agents:
            return jsonify({"error": "Agent not found"}), 404

        exec_template = read_template_file("Exec_Bash_Template.sh")
        executor_script_content = exec_template.safe_substitute(command=command)
        executor_script_path = PAYLOADS_DIR / "dynamic_payload.sh"
        executor_script_path.write_text(executor_script_content)
        payloads.append("dynamic_payload.sh")

        command_id = str(uuid.uuid4())
        instruction = Instruction(
            id=command_id,
            command=encode_base64("./dynamic_payload.sh"),
            executor="sh",
            timeout=60,
            payloads=payloads,
            uploads=[],
            delete_payload=True,
        )
        command = Command(
            id=command_id,
            instructions=instruction,
            status=CommandStatus.PENDING,
            result=None,
        )

        # Add command to queue and create result tracking
        command_queues[agent].append(instruction)
        command_results[command_id] = command

        return jsonify(command.model_dump())

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# Check command status
@app.route("/command_status/<command_id>", methods=["GET"])
def check_command_status(command_id):
    if command_id not in command_results:
        return jsonify({"error": "Command not found"}), 404

    command = command_results[command_id]
    return jsonify(command.model_dump())


# Download file
@app.route("/file/download", methods=["POST"])
def download():
    try:
        file_name = request.headers.get("File")

        if not file_name:
            return jsonify({"error": "Missing file name"}), 400

        # Try both payload directories
        file_path = BASE_DIR / "payloads" / file_name
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404

        file_data = file_path.read_bytes()

        headers = {
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "FILENAME": file_name,
        }

        return file_data, 200, headers

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# Download file
@app.route("/agent/download", methods=["POST"])
def agent_download():
    try:
        file_name = request.headers.get("File")

        if not file_name:
            return jsonify({"error": "Missing file name"}), 400

        file_path = AGENTS_DIR / file_name
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404

        file_data = file_path.read_bytes()

        headers = {
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "FILENAME": file_name,
        }

        return file_data, 200, headers

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# Stream action logs
@app.route("/stream_action_logs", methods=["GET"])
def stream_action_logs():
    def generate_log_stream():
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
                try:
                    latest_log_path = get_latest_log_path()[0]
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
                try:
                    with open(current_log_path, "r") as f:
                        f.seek(position)
                        for line in f:
                            try:
                                log_entry = json.loads(line)
                                if log_entry.get("type") == "LowLevelAction":
                                    yield f"data: {line.strip()}\n\n"
                            except json.JSONDecodeError:
                                continue
                        position = f.tell()
                except FileNotFoundError:
                    yield f"data: {json.dumps({'error': 'Log file not found, waiting...'})}\n\n"
            else:
                yield f"data: {json.dumps({'status': 'No log file available yet'})}\n\n"

            time.sleep(1)

    # Set appropriate headers for SSE
    return Response(
        stream_with_context(generate_log_stream()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


# Stream llm logs
@app.route("/stream_llm_logs", methods=["GET"])
def stream_llm_logs():
    def generate_log_stream():
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
                try:
                    latest_log_path = get_latest_log_path()[1]
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
                try:
                    with open(current_log_path, "r") as f:
                        f.seek(position)
                        for line in f:
                            yield f"data: {line.strip()}\n\n"
                        position = f.tell()
                except FileNotFoundError:
                    yield f"data: {json.dumps({'error': 'Log file not found, waiting...'})}\n\n"
            else:
                yield f"data: {json.dumps({'status': 'No log file available yet'})}\n\n"

            time.sleep(1)

    # Set appropriate headers for SSE
    return Response(
        stream_with_context(generate_log_stream()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


# Incalmo startup
@app.route("/startup", methods=["POST"])
def incalmo_startup():
    try:
        data = request.get_data()
        json_data = json.loads(data)

        # Validate using AttackerConfig schema
        try:
            config = AttackerConfig(**json_data)
        except Exception as validation_error:
            return jsonify(
                {"error": "Invalid configuration", "details": str(validation_error)}
            ), 400

        strategy_name = config.strategy.llm
        print(f"[FLASK] Starting Celery task for strategy: {strategy_name}")

        # Use the imported task function
        task = run_incalmo_strategy_task.delay(strategy_name)
        task_id = task.id

        # Cancel any existing strategy with the same name
        if strategy_name in running_strategy_tasks:
            old_task_id = running_strategy_tasks[strategy_name]
            print(f"[FLASK] Cancelling existing task: {old_task_id}")
            celery.control.revoke(old_task_id, terminate=True)

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

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 400
    except Exception as e:
        print(f"[FLASK] Error starting strategy: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Failed to start Incalmo server: {str(e)}"}), 500


# Check strategy status
@app.route("/strategy_status/<strategy_name>", methods=["GET"])
def strategy_status(strategy_name):
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


# Check task status by task ID
@app.route("/task_status/<task_id>", methods=["GET"])
def task_status(task_id):
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


# Cancel strategy
@app.route("/cancel_strategy/<strategy_name>", methods=["POST"])
def cancel_strategy(strategy_name):
    if strategy_name not in running_strategy_tasks:
        return jsonify({"error": "Strategy not found"}), 404

    task_id = running_strategy_tasks[strategy_name]

    try:
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

    except Exception as e:
        print(f"[FLASK] Error cancelling strategy {strategy_name}: {e}")
        return jsonify(
            {"error": f"Failed to cancel strategy: {str(e)}", "task_id": task_id}
        ), 500


# List all running strategies
@app.route("/running_strategies", methods=["GET"])
def list_strategies():
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


# Health check
@app.route("/health", methods=["GET"])
def health_check():
    # Check if Celery workers are available
    inspector = celery.control.inspect()
    active_workers = inspector.active()

    return jsonify(
        {
            "status": "healthy",
            "server": "Flask + Celery",
            "celery_workers": len(active_workers) if active_workers else 0,
            "running_strategies": len(running_strategy_tasks),
            "broker": app.config.get("CELERY_BROKER_URL"),
        }
    ), 200


@app.route("/available_strategies", methods=["GET"])
def get_available_strategies():
    """Get all available strategies from the registry"""
    try:
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

    except Exception as e:
        return jsonify({"error": f"Failed to get strategies: {str(e)}"}), 500


@app.route("/", methods=["GET"])
def api_root():
    return jsonify(
        {
            "message": "Incalmo C2 Server API",
        }
    )


if __name__ == "__main__":
    if DEBUG:
        print(f"[DEBUG] Starting debug server on port {DEBUG_PORT}")
        debugpy.listen(("0.0.0.0", DEBUG_PORT))
        print(f"[DEBUG] Waiting for debugger to attach on port {DEBUG_PORT}...")
        debugpy.wait_for_client()
        print("[DEBUG] Debugger attached!")
    app.run(host="0.0.0.0", port=8888, debug=True if not DEBUG else False)
