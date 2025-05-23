from incalmo.core.strategies.llm.llm_strategy import LLMStrategy

from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.core.strategies.llm.interfaces.gemini_2_flash import (
    Gemini2FlashInterface,
)

from enum import Enum


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class Gemini2FlashStrategy(LLMStrategy, name="gemini_2_flash_strategy"):
    def create_llm_interface(self) -> LLMInterface:
        return Gemini2FlashInterface(
            self.logging_service, self.environment_state_service, self.config
        )
