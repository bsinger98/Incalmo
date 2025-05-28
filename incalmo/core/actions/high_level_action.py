from abc import ABC, abstractmethod

from incalmo.core.services import (
    LowLevelActionOrchestrator,
    EnvironmentStateService,
    AttackGraphService,
)
from incalmo.core.models.events import Event


class HighLevelAction(ABC):
    def __str__(self):
        def format_value(value):
            if isinstance(value, list):
                return "[" + ", ".join(str(v) for v in value) + "]"
            return str(value)

        params = ", ".join(
            f"{key}={repr(format_value(value))}" for key, value in self.__dict__.items()
        )
        return f"{self.__class__.__name__}: {params}"

    @abstractmethod
    async def run(
        self,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
    ) -> list[Event]:
        return []
