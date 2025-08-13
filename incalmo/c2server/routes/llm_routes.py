"""
LLM-related routes for the C2 server.
Handles LLM agent action queue management.
"""

import json
from flask import Blueprint, request, jsonify

from incalmo.c2server.shared import llm_agent_actions

# Create blueprint
llm_bp = Blueprint("llm", __name__)


@llm_bp.route("/start_llm_agent_action", methods=["POST"])
def add_llm_agent_action():
    """Add an LLM agent action to the queue."""
    data = request.data
    json_data = json.loads(data)
    if not json_data or "action" not in json_data:
        return jsonify({"error": "Invalid request data"}), 400

    llm_agent_actions.append(json_data)

    return jsonify(
        {"status": "success", "message": f"Action {json_data['action']} added"}
    ), 200


@llm_bp.route("/get_llm_agent_action", methods=["GET"])
def get_llm_agent_action():
    """Get the next LLM agent action from the queue."""
    if not llm_agent_actions:
        return jsonify({"error": "No LLM Agent actions in queue"}), 404

    action = llm_agent_actions.pop(0)
    return jsonify(action), 200
