from incalmo.core.strategies.llm.llm_strategy import LLMStrategy

from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.core.strategies.llm.interfaces.gemini_15_pro_interface import (
    Gemini15ProInterface,
)

from enum import Enum

import anthropic

client = anthropic.Anthropic()


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class Gemini15ProStrategy(LLMStrategy, name="gemini_15_pro_strategy"):
    def create_llm_interface(self) -> LLMInterface:
        return Gemini15ProInterface(
            self.logger, self.environment_state_service, self.config
        )
