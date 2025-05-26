from incalmo.core.strategies.llm.llm_strategy import LLMStrategy

from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.core.strategies.llm.interfaces.deepseek7b import (
    DeepSeek7bInterface,
)

from enum import Enum

import anthropic

client = anthropic.Anthropic()


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class Deepseek7bStrategy(LLMStrategy, name="deepseek7b_strategy"):
    def create_llm_interface(
        self,
    ) -> LLMInterface:
        return DeepSeek7bInterface(
            self.logging_service, self.environment_state_service, self.config
        )
