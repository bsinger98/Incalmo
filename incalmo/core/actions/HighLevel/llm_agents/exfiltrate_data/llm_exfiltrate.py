from incalmo.core.models.attacker.agent import Agent
import os
from string import Template

from incalmo.core.actions.HighLevel.llm_agents.llm_agent_action import (
    LLMAgentAction,
)
from incalmo.core.actions.LowLevel import (
    RunBashCommand,
)

from incalmo.core.models.events import Event, BashOutputEvent
from incalmo.core.models.network import Host
from incalmo.core.services import (
    LowLevelActionOrchestrator,
    EnvironmentStateService,
    AttackGraphService,
)
from incalmo.core.services.action_context import HighLevelContext


class LLMExfiltrateData(LLMAgentAction):
    def __init__(self, host: Host):
        self.host = host
        # get_preprompt depends on source_host and target_host
        super().__init__()

    async def run(
        self,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
        context: HighLevelContext,
    ) -> list[Event]:
        events = []

        all_agents = environment_state_service.get_agents()
        agents_str = create_agent_selection_str(all_agents)

        attacker_host = environment_state_service.initial_hosts[0]
        if len(environment_state_service.initial_hosts) == 0:
            raise Exception("No initial agents found in environment state service")
        attacker_agent = agent_to_str(attacker_host.agents[0])

        # Update preprompt with C2C server
        preprompt = self.llm_agent.get_preprompt()
        preprompt = preprompt = Template(preprompt).safe_substitute(
            {
                "agents": agents_str,
                "attacker_agent": attacker_agent,
                "files": self.host.critical_data_files,
                "host": self.host,
            }
        )
        self.llm_agent.set_preprompt(preprompt)

        cur_response = ""

        for i in range(self.MAX_CONVERSATION_LEN):
            new_msg = self.llm_agent.send_message(cur_response)

            if "<finished>" in new_msg:
                break

            bash_cmd = self.llm_agent.extract_tag(new_msg, "bash")
            agent_num = self.llm_agent.extract_tag(new_msg, "agent")
            new_events = []

            if not bash_cmd or not agent_num:
                break

            # Agent number validation
            try:
                agent_num = int(agent_num)
            except ValueError:
                cur_response = "Invalid agent number"
                continue

            if agent_num < 0 or agent_num >= len(all_agents):
                cur_response = "Invalid agent number"
                continue

            bash_output = ""
            error = None
            try:
                new_events = await low_level_action_orchestrator.run_action(
                    RunBashCommand(all_agents[agent_num], bash_cmd), context
                )
            except Exception as e:
                error = e

            if error:
                cur_response = f"Error running exploit: {str(error)}"
                continue

            for event in new_events:
                if isinstance(event, BashOutputEvent):
                    bash_output += event.bash_output
            cur_response = "Bash command output:\n" + bash_output

        return events

    def get_preprompt(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        preprompt: str = ""
        with open(os.path.join(cur_dir, "preprompt.txt"), "r") as preprompt_file:
            preprompt = preprompt_file.read()
        return preprompt


def create_agent_selection_str(agents: list[Agent]):
    agent_str = ""
    for i in range(0, len(agents)):
        agent = agent_to_str(agents[i])
        agent_str += f"{i}: {agent}\n"

    return agent_str


def agent_to_str(agent: Agent):
    return f"id: {agent.paw}, hostname: {agent.hostname}, user: {agent.username}, ip_adrs: {agent.host_ip_addrs}"
