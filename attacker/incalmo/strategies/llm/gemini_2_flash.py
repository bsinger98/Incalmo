from incalmo.strategies.llm.llm_strategy import LLMStrategy

from incalmo.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.strategies.llm.interfaces.gemini_2_flash import (
    Gemini2FlashInterface,
)

from enum import Enum


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class Gemini2FlashStrategy(LLMStrategy):
    def create_llm_interface(self) -> LLMInterface:
        return Gemini2FlashInterface(None, self.environment_state_service, self.config)
