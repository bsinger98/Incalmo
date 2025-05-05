import random
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService

from plugins.deception.app.strategies.perry_strategy import PerryStrategy

from plugins.deception.app.actions.HighLevel import EscelatePrivledge
from enum import Enum


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class LogicalPlanner(PerryStrategy):
    def __init__(
        self,
        operation: Operation,
        planning_svc: PlanningService,
        stopping_conditions=(),
    ):
        super().__init__(operation, planning_svc, stopping_conditions)

        self.state = EquifaxAttackerState.InitialAccess

    async def step(self) -> bool:
        for host in self.environment_state_service.network.get_all_hosts():
            events = await self.high_level_action_orchestrator.run_action(
                EscelatePrivledge(host)
            )
            print("Events: ")
            for event in events:
                print(event)

        return True
