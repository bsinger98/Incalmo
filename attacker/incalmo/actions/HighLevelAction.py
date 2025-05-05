from abc import ABC, abstractmethod

from plugins.deception.app.services import (
    LowLevelActionOrchestrator,
    EnvironmentStateService,
    AttackGraphService,
)
from plugins.deception.app.models.events import Event


class HighLevelAction(ABC):
  
    def __str__(self):
      params = ", ".join(f"{key}={repr(value)}" for key, value in self.__dict__.items())
      return f"{self.__class__.__name__}: {params}"
    
    @abstractmethod
    async def run(
        self,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
    ) -> list[Event]:
        return []
      
    
