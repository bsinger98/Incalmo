from incalmo.core.actions.HighLevel.llm_agents import (
    LLMAgentScan,
    LLMLateralMove,
    LLMPrivilegeEscalate,
    LLMFindInformation,
    LLMExfiltrateData,
)
from incalmo.core.actions.HighLevel.llm_agents.llm_agent_action import LLMAgentAction
from incalmo.models.llm_agent_action_data import LLMAgentActionData


class LLMAgentRegistry:
    def __init__(self):
        self.agent_registry = {
            "scan": LLMAgentScan,
            "lateral_move": LLMLateralMove,
            "privilege_escalation": LLMPrivilegeEscalate,
            "find_information": LLMFindInformation,
            "exfiltrate": LLMExfiltrateData,
        }

    def get_llm_agent_action(self, action_data: LLMAgentActionData) -> LLMAgentAction:
        """
        Retrieves an LLM agent action class by its name.
        """
        if action_data.action in self.agent_registry:
            return self.agent_registry[action_data.action]
        else:
            raise ValueError(f"LLM agent action '{action_data.action}' not found.")
