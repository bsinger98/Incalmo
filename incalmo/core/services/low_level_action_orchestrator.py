from incalmo.core.actions.low_level_action import LowLevelAction
from incalmo.core.models.attacker.agent import Agent
from incalmo.api.server_api import C2ApiClient
from incalmo.core.models.events.Event import Event

# TODO Fix these imports
# from incalmo.services.environment_state_service import (
#     EnvironmentStateService,
# )
from incalmo.core.models.events import InfectedNewHost, RootAccessOnHost
from incalmo.core.services.logging_service import PerryLogger


class LowLevelActionOrchestrator:
    def __init__(
        self,
        logging_service: PerryLogger,
        # environment_state_service: EnvironmentStateService,
    ):
        # self.environment_state_service = environment_state_service
        self.logger = logging_service.setup_logger(logger_name="low_level_action")

    async def run_action(self, low_level_action: LowLevelAction) -> list[Event]:
        self.logger.info(f"Low_level_action: \n{str(low_level_action)}")
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
        self.logger.info(
            "Events generated:\n" + "\n".join(str(event) for event in events)
        )
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
