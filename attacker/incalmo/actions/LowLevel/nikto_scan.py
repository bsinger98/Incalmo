from ..low_level_action import LowLevelAction
from models.attacker.agent import Agent

from models.events import Event, VulnerableServiceFound


class NiktoScan(LowLevelAction):
    def __init__(self, agent: Agent, host: str, port: int, service: str):
        self.host = host
        self.port = port
        self.service = service

        command = f"nikto -h {host} -p {port} -maxtime 10s -timeout 3"
        super().__init__(agent, command)

    async def get_result(
        self,
        stdout: str | None,
        stderr: str | None,
    ) -> list[Event]:
        if stdout is None:
            return []
        
        if "CVE-2017-5638" in stdout:
            return [
                VulnerableServiceFound(
                    port=self.port,
                    host=self.host,
                    service=self.service,
                    cve="CVE-2017-5638",
                )
            ]

        return []
