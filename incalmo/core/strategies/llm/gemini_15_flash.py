from incalmo.core.strategies.llm.llm_strategy import LLMStrategy

from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.core.strategies.llm.interfaces.gemini_15_flash import (
    Gemini15FlashInterface,
)
from enum import Enum


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class Gemini15FlashStrategy(LLMStrategy, name="gemini_15_flash_strategy"):
    def create_llm_interface(self) -> LLMInterface:
        return Gemini15FlashInterface(
            self.logging_service, self.environment_state_service, self.config
        )
