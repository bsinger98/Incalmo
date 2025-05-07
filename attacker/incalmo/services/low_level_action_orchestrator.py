from attacker.incalmo.actions.low_level_action import LowLevelAction
from models.events.Event import Event

from helpers.ability_helpers import run_ability
from helpers.agent_helpers import get_trusted_agents
from services.environment_state_service import (
    EnvironmentStateService,
)
from models.events import InfectedNewHost, RootAccessOnHost


class LowLevelActionOrchestrator:
    def __init__(
        self,
        environment_state_service: EnvironmentStateService,
    ):
        self.environment_state_service = environment_state_service
        self.low_level_action_log: list[tuple[str, list[str]]] = []

    def run_action(self, low_level_action: LowLevelAction) -> list[Event]:
        # Get prior agents

        # Run action with C2C server and get result

        # Check for any new agents
       
        return []

    def check_new_agents(
        self, ability_agent: Agent, prior_agents: list[Agent], post_agents: list[Agent]
    ):
        new_agent = None
        # Find the agent that was added to the operation
        for post_agent in post_agents:
            # If the agent paw was not in the prior agents, then it was added
            if post_agent.paw not in [prior_agent.paw for prior_agent in prior_agents]:
                new_agent = post_agent
                break

        if new_agent:
            # If new agent on same host as ability agent, privledge escalation was successful
            if new_agent.host == ability_agent.host:
                if new_agent.username == "root":
                    return [RootAccessOnHost(new_agent)]
            if new_agent.host != ability_agent.host:
                return [InfectedNewHost(ability_agent, new_agent)]

        return []
