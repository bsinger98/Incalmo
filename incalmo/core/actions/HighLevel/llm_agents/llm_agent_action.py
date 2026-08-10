from abc import abstractmethod, ABC
from typing import Any, Dict
from incalmo.core.actions.high_level_action import HighLevelAction
from incalmo.core.strategies.llm.interfaces.llm_agent_interface import LLMAgentInterface


class LLMAgentAction(HighLevelAction, ABC):
    def __init__(self, llm_interface: LLMAgentInterface) -> None:
        super().__init__()

        self.MAX_CONVERSATION_LEN = 10
        self.llm_interface = llm_interface

    @abstractmethod
    def get_preprompt(self) -> str:
        """
        Returns the preprompt string.
        """
        pass

    @classmethod
    @abstractmethod
    def from_params(
        cls, params: Dict[str, Any], llm_interface: LLMAgentInterface
    ) -> "LLMAgentAction":
        """Create instance from params dictionary"""
        pass

    def get_llm_conversation(self) -> str:
        # Name of the class
        class_name = self.__class__.__name__

        conversation = f"##### {class_name} Conversation: #####\n"
        conversation += self.llm_interface.conversation_to_string()
        return conversation
