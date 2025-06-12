from ..low_level_action import LowLevelAction
from incalmo.core.models.attacker.agent import Agent
from incalmo.models.command_result import CommandResult

from incalmo.core.models.events import Event, VulnerableServiceFound


class NiktoScan(LowLevelAction):
    def __init__(
        self,
        agent: Agent,
        host: str,
        port: int,
        service: str,
        high_level_action_id: str,
    ):
        self.host = host
        self.port = port
        self.service = service

        command = f"nikto -h {host} -p {port} -maxtime 10s -timeout 3"
        super().__init__(agent, command, high_level_action_id=high_level_action_id)

    async def get_result(
        self,
        result: CommandResult,
    ) -> list[Event]:
        if result.output is None:
            return []

        if "CVE-2017-5638" in result.output:
            return [
                VulnerableServiceFound(
                    port=self.port,
                    host=self.host,
                    service=self.service,
                    cve="CVE-2017-5638",
                )
            ]

        return []
