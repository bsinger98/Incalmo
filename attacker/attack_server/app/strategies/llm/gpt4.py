from plugins.deception.app.actions.HighLevel import *
from plugins.deception.app.models.network import *
from plugins.deception.app.models.events import *
from plugins.deception.app.strategies.llm.llm_strategy import LLMStrategy

from plugins.deception.app.strategies.llm.interfaces.llm_interface import LLMInterface
from plugins.deception.app.strategies.llm.interfaces.gpt4_interface import GPT4Interface

from enum import Enum

import anthropic

client = anthropic.Anthropic()


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class LogicalPlanner(LLMStrategy):
    def create_llm_interface(self) -> LLMInterface:
        return GPT4Interface(self.llm_logger, self.environment_state_service, self.config)
