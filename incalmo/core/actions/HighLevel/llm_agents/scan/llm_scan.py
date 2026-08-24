import os
from string import Template
import json
from typing import Any, Dict

from incalmo.core.actions.high_level_action import HighLevelAction
from incalmo.core.actions.HighLevel.llm_agents.llm_agent_action import (
    LLMAgentAction,
)
from incalmo.core.actions.LowLevel import (
    RunBashCommand,
)

from incalmo.core.models.events import Event
from incalmo.core.models.events.scan_report_event import ScanReportEvent
from incalmo.core.models.network import Host, Subnet
from incalmo.core.services import (
    LowLevelActionOrchestrator,
    EnvironmentStateService,
    AttackGraphService,
)


from incalmo.core.models.network import ScanResults
from incalmo.core.services.action_context import HighLevelContext
from incalmo.core.strategies.llm.interfaces.llm_agent_interface import LLMAgentInterface


class LLMAgentScan(LLMAgentAction):
    def __init__(
        self,
        scan_host: Host,
        subnets_to_scan: list[Subnet],
        llm_interface: LLMAgentInterface,
    ):
        self.scan_host = scan_host
        self.subnets_to_scan = subnets_to_scan
        self.llm_interface = llm_interface
        self.llm_interface.set_preprompt(self.get_preprompt())
        super().__init__(llm_interface)

    @classmethod
    def from_params(
        cls, params: Dict[str, Any], llm_interface: LLMAgentInterface
    ) -> "LLMAgentScan":
        scan_host = llm_interface.environment_state_service.network.find_host_by_ip(
            params["scan_host"]
        )
        subnets_to_scan = [
            llm_interface.environment_state_service.network.find_subnet_by_host(
                scan_host
            )
        ]
        return cls(scan_host, subnets_to_scan, llm_interface)

    async def run(
        self,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
        context: HighLevelContext,
    ) -> list[Event]:
        events = []
        scan_agent = self.scan_host.get_agent()
        if not scan_agent:
            return events

        cur_response = "Start the scan"

        for i in range(self.MAX_CONVERSATION_LEN):
            new_msg = self.llm_interface.send_message(cur_response)

            bash_cmd = self.llm_interface.extract_tag(new_msg, "bash")
            if not bash_cmd or "<finished>" in new_msg:
                break

            output = await low_level_action_orchestrator.run_action(
                RunBashCommand(scan_agent, bash_cmd), context
            )

            if len(output) == 0:
                cur_response = "Bash command timed out.\n"
            else:
                bash_output = output[0].bash_output  # type: ignore
                cur_response = "Bash command output:\n" + bash_output

        # Get final scan results
        raw_scan_report = self.llm_interface.extract_tag(
            self.llm_interface.get_last_message(), "report"
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
