from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import json
import base64
import psutil
import binascii
import asyncio
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
from incalmo.c2server.celery.celery_tasks import run_incalmo_strategy_task
from incalmo.c2server.celery.celery_worker import celery_worker

from incalmo.core.strategies.incalmo_strategy import IncalmoStrategy

from incalmo.models.command import Command, CommandStatus
from incalmo.models.command_result import CommandResult
from incalmo.incalmo_runner import run_incalmo_strategy
from config.attacker_config import AttackerConfig

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

# Store agents and their pending commands
agents = {}
command_queues = defaultdict(list)
command_results: dict[str, Command] = {}

# Store running strategy tasks
running_strategy_tasks: Dict[str, str] = {}  # strategy_name -> task_id


def decode_base64(data):
    return base64.b64decode(data).decode("utf-8")


def encode_base64(data):
    return str(base64.b64encode(json.dumps(data).encode()), "utf-8")


def read_template_file(filename):
    template_path = TEMPLATE_PAYLOADS_DIR / filename
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {filename}")
    return Template(template_path.read_text())


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
    if paw not in agents:
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

    response = {
        "paw": paw,
        "sleep": 3,
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
                "infected_by": data.get("infected_by"),
            }
        except (binascii.Error, UnicodeDecodeError) as exc:
            raise ValueError(f"Invalid base64 data: {exc!r}")
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON: {exc!r}")

    return jsonify(agents_list)


# Report infection source
@app.route("/report_infection_source", methods=["POST"])
def report_infection_source():
    try:
        data = request.data
        json_data = json.loads(data)

        source_agent_paw = json_data.get("source_agent")
        new_agent_paw = json_data.get("new_agent")

        if not source_agent_paw or not new_agent_paw:
            return jsonify({"error": "Missing source or target paw"}), 400

        if source_agent_paw not in agents or new_agent_paw not in agents:
            return jsonify({"error": "Source or target agent not found"}), 404

        agents[new_agent_paw]["infected_by"] = source_agent_paw

        # Here you would typically log the infection event or update the state
        print(f"[DEBUG] Reporting infection from {source_agent_paw} to {new_agent_paw}")

        return jsonify(
            {"status": "success", "message": "Infection source reported"}
        ), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


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
        "state": task.state,
        "info": task_info,
    }

    if task.state == "PENDING":
        response["status"] = "Task is waiting to be processed"
    elif task.state == "PROGRESS":
        response["status"] = task_info.get("status", "In progress")
        response["current"] = task_info.get("current", 0)
        response["total"] = task_info.get("total", 100)
    elif task.state == "SUCCESS":
        response["status"] = "Task completed successfully"
        response["result"] = task_info
    elif task.state == "FAILURE":
        response["status"] = "Task failed"
        response["error"] = task_info.get("error", str(task.info))

    return jsonify(response), 200


# Check task status by task ID
@app.route("/task_status/<task_id>", methods=["GET"])
def task_status(task_id):
    task = run_incalmo_strategy_task.AsyncResult(task_id)

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

    response = {"task_id": task_id, "state": task.state, "info": task_info}

    if task.state == "PENDING":
        response["status"] = "Task is waiting to be processed"
    elif task.state == "PROGRESS":
        response["status"] = task_info.get("status", "In progress")
    elif task.state == "SUCCESS":
        response["status"] = "Task completed successfully"
        response["result"] = task_info
    elif task.state == "FAILURE":
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
                "status": "cancelled",
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

        # Safely handle task.info to avoid serialization errors
        task_info = {}
        if task.info:
            try:
                if isinstance(task.info, dict):
                    task_info = task.info
                elif isinstance(task.info, Exception):
                    task_info = {
                        "error": str(task.info),
                        "type": type(task.info).__name__,
                    }
                else:
                    task_info = {"info": str(task.info)}
            except Exception as e:
                task_info = {"serialization_error": str(e)}

        strategies[strategy_name] = {
            "task_id": task_id,
            "state": task.state,
            "info": task_info,
        }

        # Mark completed/failed/revoked strategies for cleanup
        if task.state in ["SUCCESS", "FAILURE", "REVOKED"]:
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
            strategy_info = {
                "name": strategy_name,
            }
            strategies.append(strategy_info)
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
    app.run(host="0.0.0.0", port=8888, debug=True)
