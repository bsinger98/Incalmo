from incalmo.core.strategies.llm.llm_strategy import LLMStrategy

from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.core.strategies.llm.interfaces.haiku3_5_interface import (
    Haiku3_5Interface,
)

from enum import Enum

import anthropic

client = anthropic.Anthropic()


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class LogicalPlanner(LLMStrategy):
    def create_llm_interface(self) -> LLMInterface:
        return Haiku3_5Interface(
            self.llm_logger, self.environment_state_service, self.config
        )
