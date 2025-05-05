import re

from plugins.deception.app.actions.LowLevelAction import LowLevelAction

from app.objects.c_agent import Agent
from app.service.knowledge_svc import KnowledgeService
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService

from plugins.deception.app.models.events import Event, SudoVersion


class GetSudoVersion(LowLevelAction):
    ability_name = "deception-runbashcommand"

    def __init__(self, agent: Agent):
        command = "sudo -V"
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
        # Regular expression to match version numbers
        version_pattern = re.compile(r"version\s([\d.]+p?\d*)")
        # Find and check all version numbers
        versions = version_pattern.findall(output)
        for version in versions:
            pattern = r"^(\d+)\.(\d+)\.(\d+)(?:p(\d+))?$"
            match = re.match(pattern, version)
            if match:
                return [SudoVersion(self.agent, version)]

        return []
