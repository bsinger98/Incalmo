"""
Command-related routes for the C2 server.
Handles command execution and status tracking.
"""

import json
import os
import uuid
from flask import Blueprint, request, jsonify

from incalmo.models.instruction import Instruction
from incalmo.models.command import Command, CommandStatus
from incalmo.c2server.shared import (
    agents,
    command_queues,
    command_results,
    encode_base64,
    read_template_file,
    PAYLOADS_DIR,
)

# Suffix payload filenames with the host-side C2C port so parallel containers
# (each mapped to a different host port) don't overwrite each other's scripts.
_PORT_SUFFIX = os.getenv("C2C_PORT", "8888")

# Create blueprint
command_bp = Blueprint("command", __name__)


@command_bp.route("/send_manual_command", methods=["POST"])
def send_manual_command():
    """Send a manual command to an agent."""
    data = request.data
    json_data = json.loads(data)
    agent_paw = json_data.get("agent")
    command = json_data.get("command")

    if not agent_paw or not command:
        return jsonify({"error": "Missing agent or command"}), 400

    if agent_paw not in agents:
        return jsonify({"error": "Agent not found"}), 404

    # Create a command directly without using the API client
    exec_template = read_template_file("Exec_Bash_Template.sh")
    executor_script_content = exec_template.safe_substitute(command=command)
    manual_payload_name = f"manual_command_{_PORT_SUFFIX}.sh"
    executor_script_path = PAYLOADS_DIR / manual_payload_name
    executor_script_path.write_text(executor_script_content)

    command_id = str(uuid.uuid4())
    instruction = Instruction(
        id=command_id,
        command=encode_base64(f"./{manual_payload_name}"),
        executor="sh",
        timeout=60,
        payloads=[manual_payload_name],
        uploads=[],
        delete_payload=True,
    )
    command_obj = Command(
        id=command_id,
        instructions=instruction,
        status=CommandStatus.PENDING,
        result=None,
    )

    # Add command to queue and create result tracking
    command_queues[agent_paw].append(instruction)
    command_results[command_id] = command_obj

    return jsonify(command_obj.model_dump())


@command_bp.route("/send_command", methods=["POST"])
def send_command():
    """Send a command to a specific agent."""
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
    dynamic_payload_name = f"dynamic_payload_{_PORT_SUFFIX}.sh"
    executor_script_path = PAYLOADS_DIR / dynamic_payload_name
    executor_script_path.write_text(executor_script_content)
    payloads.append(dynamic_payload_name)

    command_id = str(uuid.uuid4())
    instruction = Instruction(
        id=command_id,
        command=encode_base64(f"./{dynamic_payload_name}"),
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


@command_bp.route("/command_status/<command_id>", methods=["GET"])
def check_command_status(command_id):
    """Check the status of a command by its ID."""
    if command_id not in command_results:
        return jsonify({"error": "Command not found"}), 404

    command = command_results[command_id]
    return jsonify(command.model_dump())
