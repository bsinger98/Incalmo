import os
from pydantic import ValidationError
import json

from incalmo.core.models.attacker.agent import Agent
from incalmo.core.actions.HighLevel.llm_agents.llm_agent_action import (
    LLMAgentAction,
)
from incalmo.core.actions.LowLevel import (
    RunBashCommand,
)

from incalmo.core.models.events import (
    Event,
    SSHCredentialFound,
    CriticalDataFound,
)
from incalmo.core.models.network import Host, Subnet
from incalmo.core.services import (
    LowLevelActionOrchestrator,
    EnvironmentStateService,
    AttackGraphService,
)


from incalmo.core.actions.HighLevel.llm_agents.find_information.info_report import (
    FindInformationResult,
    Credential,
    CriticalData,
)
from incalmo.core.services.action_context import HighLevelContext


class LLMFindInformation(LLMAgentAction):
    def __init__(
        self,
        host: Host,
        user: str,
    ):
        super().__init__()
        self.host = host
        self.user = user

    async def run(
        self,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
        context: HighLevelContext,
    ) -> list[Event]:
        events = []
        agent = self.host.get_agent_by_username(self.user)
        if not agent:
            return events

        cur_response = ""
        for i in range(self.MAX_CONVERSATION_LEN):
            new_msg = self.llm_agent.send_message(cur_response)

            bash_cmd = self.llm_agent.extract_tag(new_msg, "bash")
            if not bash_cmd or "<finished>" in new_msg:
                break

            output = await low_level_action_orchestrator.run_action(
                RunBashCommand(agent, bash_cmd), context
            )

            if len(output) == 0:
                cur_response = "Bash command timed out.\n"
            else:
                bash_output = output[0].bash_output  # type: ignore
                cur_response = "Bash command output:\n" + bash_output

        # Get final scan results
        raw_scan_report = self.llm_agent.extract_tag(
            self.llm_agent.get_last_message(), "report"
        )

        events = []
        if raw_scan_report:
            try:
                report_json = json.loads(raw_scan_report)
                scan_results = FindInformationResult(**report_json)
                events = self.convert_result_to_event(scan_results, agent=agent)
            except json.JSONDecodeError as e:
                pass
            except ValidationError as e:
                pass

        return events

    def get_preprompt(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        preprompt: str = ""
        with open(os.path.join(cur_dir, "preprompt.txt"), "r") as preprompt_file:
            preprompt = preprompt_file.read()
        return preprompt

    def convert_result_to_event(
        self,
        results: FindInformationResult,
        agent: Agent,
    ) -> list[Event]:
        """
        Convert a result dictionary to an Event object.
        """
        events = []
        for result in results.results:
            if isinstance(result, Credential):
                events.append(
                    SSHCredentialFound(
                        agent,
                        hostname=result.hostname,
                        ssh_username=result.username,
                        ssh_host=result.host_ip,
                        port=result.port,
                    )
                )
            elif isinstance(result, CriticalData):
                events.append(
                    CriticalDataFound(
                        host=self.host, agent=agent, files_paths=result.file_paths
                    )
                )

        return events
