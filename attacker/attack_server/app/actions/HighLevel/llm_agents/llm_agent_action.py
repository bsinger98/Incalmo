from abc import abstractmethod, ABC
from plugins.deception.app.actions.HighLevelAction import HighLevelAction
from plugins.deception.app.actions.HighLevel.llm_agents.llm_agent import LLMAgent


class LLMAgentAction(HighLevelAction, ABC):
    def __init__(self) -> None:
        super().__init__()

        self.MAX_CONVERSATION_LEN = 10

        preprompt = self.get_preprompt()
        self.llm_agent = LLMAgent(preprompt)

    @abstractmethod
    def get_preprompt(self) -> str:
        """
        Returns the preprompt string.
        """
        pass

    def get_llm_conversation(self) -> str:
        # Name of the class
        class_name = self.__class__.__name__

        conversation = f"##### {class_name} Conversation: #####\n"
        conversation += self.llm_agent.conversation_to_string()
        return conversation
