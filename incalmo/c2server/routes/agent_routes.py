"""
Agent-related routes for the C2 server.
Handles agent registration, management, and deletion.
"""

import json
import uuid
from flask import Blueprint, request, jsonify

from incalmo.models.instruction import Instruction
from incalmo.models.command import Command, CommandStatus
from incalmo.models.command_result import CommandResult
from incalmo.c2server.shared import (
    agents,
    agent_deletion_queue,
    command_queues,
    command_results,
    decode_base64,
    encode_base64,
    read_template_file,
    PAYLOADS_DIR,
)

# Create blueprint
agent_bp = Blueprint("agent", __name__)


@agent_bp.route("/beacon", methods=["POST"])
def beacon():
    """Agent check-in endpoint."""
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


@agent_bp.route("/agents", methods=["GET"])
def get_agents():
    """Get list of all connected agents."""
    agents_list = {}
    for paw, data in agents.items():
        decoded_info = decode_base64(data["info"])
        parsed_info = json.loads(decoded_info)

        agents_list[paw] = {
            "paw": paw,
            "username": parsed_info.get("username"),
            "privilege": parsed_info.get("privilege"),
            "pid": parsed_info.get("pid"),
            "host_ip_addrs": parsed_info.get("host_ip_addrs"),
        }

    return jsonify(agents_list)


@agent_bp.route("/agent/delete/<paw>", methods=["DELETE"])
def delete_agent(paw):
    """Delete a specific agent by sending a kill command."""
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
