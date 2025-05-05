import random
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService
from plugins.deception.app.helpers.logging import (
    get_logger,
    log_event,
)

from plugins.deception.app.strategies.perry_strategy import PerryStrategy

from plugins.deception.app.actions.LowLevel import RunBashCommand, ReadFile
from plugins.deception.app.actions.HighLevel.llm_agents.scan.llm_scan import (
    LLMAgentScan,
)
from plugins.deception.app.actions.HighLevel import (
    LLMAgentScan,
    LLMExfiltrateData,
    LLMFindInformation,
)

from plugins.deception.app.actions.HighLevel.llm_agents.lateral_movement.llm_lateral_movement import (
    LLMLateralMove,
)

from plugins.deception.app.actions.HighLevel import Scan, LateralMoveToHost
from plugins.deception.app.models.network import Host, OpenPort
from enum import Enum

plugin_logger = get_logger()


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class LogicalPlanner(PerryStrategy):
    def __init__(
        self,
        operation: Operation,
        planning_svc: PlanningService,
        stopping_conditions=(),
    ):
        super().__init__(operation, planning_svc, stopping_conditions)

        self.state = EquifaxAttackerState.InitialAccess

        print("LogicalPlanner init")

    async def step(self) -> bool:
        agents = self.environment_state_service.get_agents()
        events = await self.low_level_action_orchestrator.run_action(
            RunBashCommand(agents[0], "ls")
        )
        # print("Events: ")
        # for event in events:
        #     print(event.bash_output)  # type: ignore

        # events = await self.high_level_action_orchestrator.run_action(
        #     LLMAgentScan(
        #         self.initial_hosts[0],
        #         self.environment_state_service.network.get_all_subnets(),
        #     )
        # )
        # print("Events: ")
        # for event in events:
        #     print(event)
        # action = LLMFindInformation(self.initial_hosts[0], "root")
        action = LLMExfiltrateData(self.initial_hosts[0])
        events = await self.high_level_action_orchestrator.run_action(action)
        print(action.get_llm_conversation())

        print("Hosts: ")
        for host in self.environment_state_service.network.get_all_hosts():
            print(host)

        print("Running step!")
        # await self.high_level_action_orchestrator.run_action(
        #     Scan(
        #         self.initial_hosts[0],
        #         self.environment_state_service.network.get_all_subnets(),
        #     )
        # )

        # for host in self.environment_state_service.network.get_all_hosts():
        #     if host.ip_address == "192.168.200.10":
        #         for port_num, port in host.open_ports.items():
        #             if "http" in port.service:
        #                 print(host)
        #                 print(port)
        #                 LLMLateralMove(
        #                     self.initial_hosts[0],
        #                     host,
        #                     port,
        #                 )

        # test_port = OpenPort(80, "http", ["CVE-2017-5638"])
        # test_host = Host("192.168.200.10", open_ports={8080: test_port})

        # await self.high_level_action_orchestrator.run_action(
        #     LLMLateralMove(
        #         self.initial_hosts[0],
        #         test_host,
        #     )
        # )

        # for host in self.environment_state_service.get_hosts_without_agents():
        #     if host.ip_address == "192.168.200.10"
        #     await self.high_level_action_orchestrator.run_action(
        #         LLMLateralMove(
        #             self.initial_hosts[0],
        #             None,
        #             None,
        #         )
        #     )
        #     break

        return True
