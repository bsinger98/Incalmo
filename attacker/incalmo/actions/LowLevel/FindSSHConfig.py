from ..LowLevelAction import LowLevelAction

from app.service.knowledge_svc import KnowledgeService
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService
from app.objects.c_agent import Agent

from plugins.deception.app.models.network import Host
from plugins.deception.app.models.events import SSHCredentialFound, Event

from plugins.deception.app.helpers.logging import log_event


def parse_ssh_config(config):
    hosts: dict[str, dict] = {}
    current_host = None

    for line in config.splitlines():
        line = line.strip()
        if line.startswith("Host "):
            current_host = line.split(" ", 1)[1]
            hosts[current_host] = {}
        elif current_host and line:
            key, value = line.split(" ", 1)
            hosts[current_host][key] = value

    return hosts


class FindSSHConfig(LowLevelAction):
    ability_name = "deception-runbashcommand"

    def __init__(self, agent: Agent):
        command = "cat ~/.ssh/config"
        facts = {"host.command.input": command}
        self.command = command

        super().__init__(agent, facts, self.ability_name)

    async def get_result(
        self,
        operation: Operation,
        planner: PlanningService,
        knowledge_svc_handle: KnowledgeService,
        raw_result: dict | None = None,
    ) -> list[Event]:
        if raw_result is None:
            return []

        config = raw_result["stdout"]
        hosts = parse_ssh_config(config)

        events = []
        for host, values in hosts.items():
            if "IdentityFile" in values:
                config_name = host
                hostname = values["HostName"]
                username = values["User"]
                if "Port" in values:
                    port = values["Port"]
                else:
                    port = "22"

                events.append(
                    SSHCredentialFound(
                        self.agent, config_name, username, hostname, port
                    )
                )

        return events
