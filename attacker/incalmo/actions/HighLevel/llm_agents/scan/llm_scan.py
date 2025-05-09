import os
from string import Template
import json

from incalmo.actions.high_level_action import HighLevelAction
from incalmo.actions.HighLevel.llm_agents.llm_agent_action import (
    LLMAgentAction,
)
from incalmo.actions.LowLevel import (
    RunBashCommand,
)

from incalmo.models.events import Event
from incalmo.models.events.scan_report import ScanReportEvent
from incalmo.models.network import Host, Subnet
from incalmo.services import (
    LowLevelActionOrchestrator,
    EnvironmentStateService,
    AttackGraphService,
)


from incalmo.actions.HighLevel.llm_agents.scan.scan_report import (
    ScanResults,
)


class LLMAgentScan(LLMAgentAction):
    def __init__(
        self,
        scan_host: Host,
        subnets_to_scan: list[Subnet],
    ):
        self.scan_host = scan_host
        self.subnets_to_scan = subnets_to_scan
        super().__init__()

    async def run(
        self,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
    ) -> list[Event]:
        events = []
        scan_agent = self.scan_host.get_agent()
        if not scan_agent:
            return events

        cur_response = ""

        for i in range(self.MAX_CONVERSATION_LEN):
            new_msg = self.llm_agent.send_message(cur_response)

            bash_cmd = self.llm_agent.extract_tag(new_msg, "bash")
            if not bash_cmd or "<finished>" in new_msg:
                break

            output = await low_level_action_orchestrator.run_action(
                RunBashCommand(scan_agent, bash_cmd)
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

        if raw_scan_report:
            report_json = json.loads(raw_scan_report)
            scan_results = ScanResults(**report_json)
            events.append(ScanReportEvent(scan_results))

        return events

    def get_preprompt(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        preprompt: str = ""
        with open(os.path.join(cur_dir, "scan_preprompt.txt"), "r") as preprompt_file:
            preprompt = preprompt_file.read()

        subnet_ips = [subnet.ip_mask for subnet in self.subnets_to_scan]
        parameters = {
            "networks": str(subnet_ips),
        }
        preprompt = Template(preprompt).substitute(parameters)
        return preprompt
