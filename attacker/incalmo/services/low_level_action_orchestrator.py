from incalmo.actions.low_level_action import LowLevelAction
from incalmo.models.attacker.agent import Agent
from api.server_api import C2ApiClient
from incalmo.models.events.Event import Event

# TODO Fix these imports
# from incalmo.services.environment_state_service import (
#     EnvironmentStateService,
# )
from incalmo.models.events import InfectedNewHost, RootAccessOnHost


class LowLevelActionOrchestrator:
    def __init__(
        self,
        # environment_state_service: EnvironmentStateService,
    ):
        # self.environment_state_service = environment_state_service
        self.low_level_action_log: list[tuple[str, list[str]]] = []

    async def run_action(self, low_level_action: LowLevelAction) -> list[Event]:
        c2client = C2ApiClient()
        # Get prior agents
        prior_agents = c2client.get_agents()
        # Run action with C2C server and get result
        command_result = c2client.send_command(low_level_action)
        # Check for any new agents
        post_agents = c2client.get_agents()
        agent_check_result = self.check_new_agents(
            low_level_action.agent, prior_agents, post_agents
        )
        events = await low_level_action.get_result(command_result)
        return events + agent_check_result

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
            if new_agent.hostname == ability_agent.hostname:
                if new_agent.username == "root":
                    return [RootAccessOnHost(new_agent)]
            if new_agent.hostname != ability_agent.hostname:
                return [InfectedNewHost(ability_agent, new_agent)]

        return []
