"""
File-related routes for the C2 server.
Handles file downloads for payloads and agents.
"""

from flask import Blueprint, request, jsonify

from incalmo.c2server.shared import BASE_DIR, AGENTS_DIR

# Create blueprint
file_bp = Blueprint("file", __name__)


@file_bp.route("/file/download", methods=["POST"])
def download():
    """Download a file from the payloads directory."""
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


@file_bp.route("/agent/download", methods=["POST"])
def agent_download():
    """Download a file from the agents directory."""
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
