from flask import Flask, request, jsonify
import json
import os
import base64
import binascii
from incalmo.models.instruction import Instruction
import uuid
from collections import defaultdict
from incalmo.models.command import Command, CommandStatus
from incalmo.models.command_result import CommandResult
from string import Template
import logging

app = Flask(__name__)
# Disable Flask's default request logging
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

# Store agents and their pending commands
agents = {}
command_queues = defaultdict(list)
command_results: dict[str, Command] = {}


def decode_base64(data):
    return base64.b64decode(data).decode("utf-8")


def encode_base64(data):
    return str(base64.b64encode(json.dumps(data).encode()), "utf-8")


def read_template_file(filename):
    template_dir = "./c2server/payloads/template_payloads"
    template_path = f"{template_dir}/{filename}"
    with open(template_path, "r") as file:
        template_content = file.read()
    template = Template(template_content)
    return template


# Agent check-in
@app.route("/beacon", methods=["POST"])
def beacon():
    data = request.data
    decoded_data = decode_base64(data)
    json_data = json.loads(decoded_data)

    paw = json_data.get("paw")
    results = json_data.get("results", [])

    if not paw:
        return jsonify({"error": "Missing agent ID"}), 400

    # Store agent info if new
    if paw not in agents:
        print(f"New agent: {paw}")
        agents[paw] = {"paw": paw, "info": data}

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
        executor_script_path = f"./c2server/payloads/dynamic_payloads/exec_script.sh"

        with open(executor_script_path, "w") as temp_script:
            temp_script.write(executor_script_content)

        payloads.append("exec_script.sh")

        command_id = str(uuid.uuid4())
        instruction = Instruction(
            id=command_id,
            command=encode_base64("./exec_script.sh"),
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
    print(command_results)
    print(command_id)
    if command_id not in command_results:
        return jsonify({"error": "Command not found"}), 404

    command = command_results[command_id]
    return jsonify(command.model_dump())


# Download file
@app.route("/file/download", methods=["POST"])
def download():
    print("download")
    try:
        file_name = request.headers.get("File")
        print(file_name)

        if not file_name:
            return jsonify({"error": "Missing file name"}), 400

        file_path = f"./c2server/payloads/{file_name}"
        # TODO fix this
        if not os.path.exists(file_path):
            file_path = f"./c2server/payloads/dynamic_payloads/{file_name}"
        with open(file_path, "rb") as f:
            file_data = f.read()

        headers = {
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "FILENAME": file_name,
        }

        return file_data, 200, headers

    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# Download file
@app.route("/agent/download", methods=["POST"])
def agent_download():
    print("agent download")
    try:
        file_name = request.headers.get("File")
        print(file_name)

        if not file_name:
            return jsonify({"error": "Missing file name"}), 400

        file_path = f"./c2server/agents/{file_name}"
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        with open(file_path, "rb") as f:
            file_data = f.read()

        headers = {
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "FILENAME": file_name,
        }

        return file_data, 200, headers

    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
