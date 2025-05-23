from incalmo.core.strategies.llm.llm_strategy import LLMStrategy

from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.core.strategies.llm.interfaces.gpt4o_mini_interface import (
    GPT4oMiniInterface,
)

from enum import Enum

import anthropic

client = anthropic.Anthropic()


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class GPT4oMiniStrategy(LLMStrategy, name="gpt4o_mini_strategy"):
    def create_llm_interface(self) -> LLMInterface:
        return GPT4oMiniInterface(
            self.logging_service, self.environment_state_service, self.config
        )
