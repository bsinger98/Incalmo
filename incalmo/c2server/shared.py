"""
Shared utilities, constants, and state for the C2 server.
Contains common code used across multiple route modules.
"""

import base64
import json
from collections import defaultdict
from enum import Enum
from pathlib import Path
from string import Template
from typing import Dict

from config.attacker_config import AttackerConfig
from incalmo.models.command import Command


# Define base directories
BASE_DIR = Path(__file__).parent
PAYLOADS_DIR = BASE_DIR / "payloads"
TEMPLATE_PAYLOADS_DIR = PAYLOADS_DIR / "template_payloads"
AGENTS_DIR = BASE_DIR / "agents"

# Store agents and their pending commands
agents = {}
agent_deletion_queue = set()
command_queues = defaultdict(list)
command_results: dict[str, Command] = {}

# Store environment info
hosts = []

# Store LLM Agent actions
llm_agent_actions = []

# Store running strategy tasks
running_strategy_tasks: Dict[str, AttackerConfig] = {}


# Enums
class TaskState(Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    REVOKED = "REVOKED"
    RETRY = "RETRY"
    RECEIVED = "RECEIVED"
    PROGRESS = "PROGRESS"

    @classmethod
    def from_string(cls, state_str):
        try:
            if not state_str or not isinstance(state_str, str):
                # If state_str is None or empty, return PENDING
                return cls.PENDING
            return cls(state_str)

        except (ValueError, KeyError, AttributeError, TypeError) as e:
            # Return default state when conversion fails
            return cls.PENDING

    def __str__(self):
        return self.value


# Utility functions
def decode_base64(data):
    """Decode base64 data to UTF-8 string."""
    return base64.b64decode(data).decode("utf-8")


def encode_base64(data):
    """Encode data as base64 string."""
    return str(base64.b64encode(json.dumps(data).encode()), "utf-8")


def read_template_file(filename):
    """Read and return a template file from the template payloads directory."""
    template_path = TEMPLATE_PAYLOADS_DIR / filename
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {filename}")
    return Template(template_path.read_text())


def get_latest_log_path(strategy_name=None, task_id=None):
    """Get the latest log file paths for a strategy."""
    output_dirs = sorted(Path("output").glob("*_*_*-*-*_*-*-*"), reverse=True)
    if not output_dirs:
        raise FileNotFoundError("No log directories found")

    matching_dirs = output_dirs

    if strategy_name:
        matching_dirs = [d for d in matching_dirs if strategy_name in d.name]
        if not matching_dirs:
            raise FileNotFoundError(
                f"No log directories found for strategy: {strategy_name}"
            )

    if task_id:
        task_dirs = [d for d in matching_dirs if task_id in d.name]
        if task_dirs:
            matching_dirs = task_dirs

    latest_dir = matching_dirs[0]

    actions_log_path = latest_dir / "actions.json"
    llm_log_path = latest_dir / "llm.log"
    llm_agent_log_path = latest_dir / "llm_agent.log"

    return actions_log_path, llm_log_path, llm_agent_log_path


def get_log_path(strategy_id: str):
    # Get all directories in the output directory
    output_dirs = sorted(Path("output").glob("*_*_*-*-*_*-*-*"), reverse=True)
    if not output_dirs:
        raise FileNotFoundError("No log directories found")

    for dir in output_dirs:
        if strategy_id in dir.name:
            return dir

    raise FileNotFoundError(f"No log directory found for strategy: {strategy_id}")
