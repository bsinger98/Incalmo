from incalmo.core.strategies.llm.llm_strategy import LLMStrategy

from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.core.strategies.llm.interfaces.gpto1_interface import (
    GPTo1Interface,
)

from enum import Enum

import anthropic

client = anthropic.Anthropic()


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class GPTo1Strategy(LLMStrategy, name="gpto1_strategy"):
    def create_llm_interface(self) -> LLMInterface:
        return GPTo1Interface(
            self.logger, self.environment_state_service, self.config
        )
