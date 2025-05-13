from incalmo.strategies.llm.llm_strategy import LLMStrategy

from incalmo.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.strategies.llm.interfaces.gpto1_interface import (
    GPTo1Interface,
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
        return GPTo1Interface(
            self.llm_logger, self.environment_state_service, self.config
        )
