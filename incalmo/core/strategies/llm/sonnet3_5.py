from incalmo.core.strategies.llm.llm_strategy import LLMStrategy

from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.core.strategies.llm.interfaces.sonnet3_5_interface import (
    Sonnet3_5_Interface,
)

from enum import Enum

import anthropic

client = anthropic.Anthropic()


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class Sonnet3_5_Strategy(LLMStrategy, name="sonnet3_5_strategy"):
    def create_llm_interface(self) -> LLMInterface:
        return Sonnet3_5_Interface(
            self.logger, self.environment_state_service, self.config
        )
