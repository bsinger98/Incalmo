import asyncio
from ..low_level_action import LowLevelAction

from app.objects.c_agent import Agent
from app.objects.secondclass.c_fact import Fact
from app.service.knowledge_svc import KnowledgeService
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService

from plugins.deception.app.models.events import Event, BashOutputEvent


class RunBashCommand(LowLevelAction):
    ability_name = "deception-runbashcommand"

    def __init__(self, agent: Agent, command: str):
        facts = {"host.command.input": command}
        self.command = command
        super().__init__(agent, facts, RunBashCommand.ability_name)

    async def get_result(
        self,
        operation: Operation,
        planner: PlanningService,
        knowledge_svc_handle: KnowledgeService,
        raw_result: dict | None = None,
    ) -> list[Event]:
        await asyncio.sleep(10)

        if raw_result is None:
            return []

        if len(raw_result["stderr"]) > 0:
            return [BashOutputEvent(self.agent, raw_result["stderr"])]

        return [BashOutputEvent(self.agent, raw_result["stdout"])]
