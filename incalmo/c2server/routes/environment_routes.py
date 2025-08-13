"""
Environment-related routes for the C2 server.
Handles environment state management and host information.
"""

import json
from flask import Blueprint, request, jsonify

from config.attacker_config import AttackerConfig
from incalmo.core.strategies.incalmo_strategy import IncalmoStrategy
from incalmo.c2server.shared import hosts

# Create blueprint
environment_bp = Blueprint("environment", __name__)


@environment_bp.route("/update_environment_state", methods=["POST"])
def update_environment_state():
    """Update the environment state with host information."""
    global hosts
    data = request.data
    json_data = json.loads(data)

    hosts = json_data.get("hosts", [])
    return jsonify({"status": "success", "message": "Infection source reported"}), 200


@environment_bp.route("/hosts", methods=["GET"])
def get_hosts():
    """Get the current list of hosts in the environment."""
    return jsonify(
        {
            "hosts": hosts,
        }
    ), 200


@environment_bp.route("/get_initial_environment", methods=["POST"])
def get_initial_environment():
    """Initialize the base environment with the provided configuration."""
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
        IncalmoStrategy.initialize_base_environment(config)
        return jsonify({"status": "success"}), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
