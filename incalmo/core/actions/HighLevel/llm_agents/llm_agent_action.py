from abc import abstractmethod, ABC
from typing import Any, Dict
from incalmo.core.actions.high_level_action import HighLevelAction
from incalmo.core.strategies.llm.interfaces.llm_agent_interface import LLMAgentInterface
from incalmo.core.services import LowLevelActionOrchestrator, EnvironmentStateService, AttackGraphService
from incalmo.core.models.events import Event
from incalmo.core.services.action_context import HighLevelContext


class LLMAgentAction(HighLevelAction, ABC):
    def __init__(self, llm_interface: LLMAgentInterface) -> None:
        super().__init__()

        self.MAX_CONVERSATION_LEN = 10
        self.llm_interface = llm_interface

    async def run(
        self,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
        context: HighLevelContext,
    ) -> list[Event]:
        self.llm_interface.action_id = context.hl_id
        self.llm_interface.action_name = self.__class__.__name__
        return await self._run(
            low_level_action_orchestrator,
            environment_state_service,
            attack_graph_service,
            context,
        )

    @abstractmethod
    async def _run(
        self,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
        context: HighLevelContext,
    ) -> list[Event]:
        pass

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
