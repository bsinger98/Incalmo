from flask import Flask, request, jsonify
import json
import base64
import binascii
import asyncio
from incalmo.models.instruction import Instruction
import uuid
from collections import defaultdict
from incalmo.models.command import Command, CommandStatus
from incalmo.models.command_result import CommandResult
from incalmo.incalmo_runner import run_incalmo_strategy
from config.attacker_config import AttackerConfig
from string import Template
import logging
from pathlib import Path

app = Flask(__name__)
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
            agents[paw] = {"paw": paw, "info": data}
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
            }
        except (binascii.Error, UnicodeDecodeError) as exc:
            raise ValueError(f"Invalid base64 data: {exc!r}")
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON: {exc!r}")

    return jsonify(agents_list)


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
async def incalmo_startup():
    try:
        data = request.data
        json_data = json.loads(data)
        # Validate using AttackerConfig schema
        try:
            config = AttackerConfig(**json_data)
        except Exception as validation_error:
            return jsonify(
                {"error": "Invalid configuration", "details": str(validation_error)}
            ), 400

        strategy = config.strategy.llm
        print(f"Starting task of strategy: {strategy}")

        asyncio.create_task(run_incalmo_strategy(strategy))

        response = {
            "status": "success",
            "message": f"Incalmo started with strategy: {strategy}",
            "config": config.model_dump(),
        }

        return jsonify(response), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to start Incalmo server: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
