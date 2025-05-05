import re

from plugins.deception.app.actions.LowLevelAction import LowLevelAction

from app.objects.c_agent import Agent
from app.service.knowledge_svc import KnowledgeService
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService

from plugins.deception.app.models.events import Event, VulnerableServiceFound


class NiktoScan(LowLevelAction):
    ability_name = "deception-runbashcommand"

    def __init__(self, agent: Agent, host: str, port: int, service: str):
        self.host = host
        self.port = port
        self.service = service

        command = f"nikto -h {host} -p {port} -maxtime 10s -timeout 3"
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

        output = raw_result["stdout"]
        if "CVE-2017-5638" in output:
            return [
                VulnerableServiceFound(
                    port=self.port,
                    host=self.host,
                    service=self.service,
                    cve="CVE-2017-5638",
                )
            ]

        return []
