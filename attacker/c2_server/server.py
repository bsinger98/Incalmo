from flask import Flask, request, jsonify, Response
import os
import json
import base64
from aiohttp import web
import Instruction
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
        print("[DEBUG] Missing agent ID")
        return jsonify({"error": "Missing agent ID"}), 400

    agent = agents.get(paw)

    if agent:
        print("[DEBUG] Agent found:", paw)
    else:
        print("[DEBUG] New Agent:", paw)
        agent = {"paw": paw, "info": data, "instructions": []}
        agents[paw] = agent

    for result in results:
        commandId = result.get("id")
        if commandId in commandEvents:
            commandEvents[commandId].set()
        output = result.get("output")
        decoded_output = decode_base64(output)

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
    agents_list = []

    for paw, _ in agents.items():
        agents_list.append(paw)

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

    instruction = Instruction.Instruction(
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
            output = result.get("output")
            decoded_output = decode_base64(output)

            agents[agent]["results"].remove(result)
            agents[agent]["instructions"].remove(instruction)
            del commandEvents[commandId]
            return jsonify({"message": "Command executed", "output": decoded_output})

    return jsonify({"message": "Command sent, no response received"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)
