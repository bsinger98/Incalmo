from incalmo.core.strategies.llm.llm_strategy import LLMStrategy

from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.core.strategies.llm.interfaces.gpt3_5_interface import (
    GPT3_5_Interface,
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
        return GPT3_5_Interface(
            self.llm_logger, self.environment_state_service, self.config
        )
