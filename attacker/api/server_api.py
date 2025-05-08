from incalmo.actions.low_level_action import LowLevelAction
from incalmo.models.attacker.agent import Agent
from config.settings import settings
import requests
import json


class Results:
    def __init__(
        self,
        message: str | None,
        agent_time: str | None,
        exit_code: str | None,
        id: str | None,
        pid: str | None,
        status: str | None,
        stdout: str | None,
        stderr: str | None,
    ):
        self.message = message
        self.agent_time = agent_time
        self.exit_code = exit_code
        self.id = id
        self.pid = pid
        self.status = status
        self.stdout = stdout
        self.stderr = stderr


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
                )
                agent_list.append(agent)
            return agent_list
        else:
            raise Exception(
                f"Failed to get agents: {response.status_code} {response.text}"
            )

    def send_command(self, low_level_action: LowLevelAction) -> Results:
        """Send a command to an agent and return the result."""
        payload = {
            "agent": low_level_action.agent.paw,
            "command": low_level_action.command,
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{self.server_url}/send_command", data=json.dumps(payload), headers=headers
        )
        if response.ok:
            # Parse the response to get the results
            result = response.json().get("results", [])
            if result:
                return Results(
                    message=result.get("message"),
                    agent_time=result.get("agent_reported_time"),
                    exit_code=result.get("exit_code"),
                    id=result.get("id"),
                    pid=result.get("pid"),
                    status=result.get("status"),
                    stdout=result.get("output"),
                    stderr=result.get("stderr"),
                )
            return Results(
                message="No results found",
            )
        else:
            raise Exception(
                f"Failed to send command: {response.status_code} {response.text}"
            )
