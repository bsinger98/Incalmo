from ..LowLevelAction import LowLevelAction
from plugins.deception.app.helpers.agent_helpers import get_trusted_agents
from plugins.deception.app.models.events import Event, InfectedNewHost

from app.objects.c_agent import Agent
from app.service.knowledge_svc import KnowledgeService
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService

from plugins.deception.app.helpers.logging import log_event

import asyncio


class SSHLateralMove(LowLevelAction):
    ability_name = "deception-ssh-copy"

    def __init__(self, agent: Agent, hostname: str):
        facts = {"host.lateralMove.sshcmd": hostname}
        super().__init__(agent, facts, SSHLateralMove.ability_name)
        self.hostname = hostname

    async def get_result(
        self,
        operation: Operation,
        planner: PlanningService,
        knowledge_svc_handle: KnowledgeService,
        raw_result: dict | None = None,
    ) -> list[Event]:
        # sleep to allow for the agent to get to the new host
        await asyncio.sleep(10)
        return []
