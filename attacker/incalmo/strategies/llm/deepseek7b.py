from incalmo.strategies.llm.llm_strategy import LLMStrategy

from incalmo.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.strategies.llm.interfaces.deepseek7b import (
    DeepSeek7bInterface,
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
        return DeepSeek7bInterface(
            self.llm_logger, self.environment_state_service, self.config
        )
