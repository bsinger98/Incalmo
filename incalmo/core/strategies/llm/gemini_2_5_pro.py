from incalmo.core.strategies.llm.llm_strategy import LLMStrategy

from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.core.strategies.llm.interfaces.gemini_2_5_pro import (
    Gemini25ProInterface,
)

from enum import Enum


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class LogicalPlanner(LLMStrategy):
    def create_llm_interface(self) -> LLMInterface:
        return Gemini25ProInterface(
            self.llm_logger, self.environment_state_service, self.config
        )
