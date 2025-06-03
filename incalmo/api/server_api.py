from incalmo.core.actions.low_level_action import LowLevelAction
from incalmo.core.models.attacker.agent import Agent
from config.settings import settings
import requests
import json
import time
from incalmo.models.command_result import CommandResult
from incalmo.models.command import Command, CommandStatus


class C2ApiClient:
    def __init__(self):
        self.server_url = settings.c2_server

    def get_agents(self) -> list[Agent]:
        """Fetch a list of agent information"""
        agent_list = []
        response = requests.get(f"{self.server_url}/agents")
        if response.ok:
            agent_data = response.json()
            for paw, info in agent_data.items():
                agent = Agent(
                    paw=paw,
                    username=info.get("username", ""),
                    privilege=info.get("privilege", ""),
                    pid=str(info.get("pid", "")),
                    host_ip_addrs=info.get("host_ip_addrs", []),
                    hostname=info.get("hostname", ""),
                )
                agent_list.append(agent)
            return agent_list
        else:
            raise Exception(
                f"Failed to get agents: {response.status_code} {response.text}"
            )

    def send_command(self, low_level_action: LowLevelAction) -> CommandResult:
        """Send a command to an agent and poll for results."""
        # Send the command
        payload = {
            "agent": low_level_action.agent.paw,
            "command": low_level_action.command,
            "payloads": low_level_action.payloads,
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{self.server_url}/send_command", data=json.dumps(payload), headers=headers
        )

        if not response.ok:
            raise Exception(
                f"Failed to send command: {response.status_code} {response.text}"
            )

        # Get command ID from initial response
        command = Command(**response.json())
        if not command:
            raise Exception("No command ID received from server")

        # Poll for results
        max_attempts = 30  # 30 seconds timeout
        poll_interval = 1  # 1 second between polls

        for _ in range(max_attempts):
            status_response = requests.get(
                f"{self.server_url}/command_status/{command.id}"
            )

            if not status_response.ok:
                raise Exception(
                    f"Failed to check command status: {status_response.status_code} {status_response.text}"
                )

            command = Command(**status_response.json())
            if command.status == CommandStatus.COMPLETED and command.result:
                return command.result

            time.sleep(poll_interval)

        raise Exception("Command polling timed out")
