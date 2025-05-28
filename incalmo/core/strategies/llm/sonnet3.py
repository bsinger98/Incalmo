from incalmo.core.strategies.llm.llm_strategy import LLMStrategy

from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.core.strategies.llm.interfaces.sonnet3_interface import (
    Sonnet3Interface,
)

from enum import Enum

import anthropic

client = anthropic.Anthropic()


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class Sonnet3Strategy(LLMStrategy, name="sonnet3_strategy"):
    def create_llm_interface(self) -> LLMInterface:
        return Sonnet3Interface(
            self.logger, self.environment_state_service, self.config
        )
