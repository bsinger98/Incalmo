import random
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService

from plugins.deception.app.strategies.perry_strategy import PerryStrategy
from plugins.deception.app.actions.HighLevel import (
    EscelatePrivledge,
    Scan,
    AttackPathLateralMove,
    FindInformationOnAHost,
    LateralMoveToHost,
    ExfiltrateData,
)
from plugins.deception.app.models.events import InfectedNewHost, SSHCredentialFound
from plugins.deception.app.strategies.util.event_util import any_events_are_type

from enum import Enum


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

    async def step(self) -> bool:
        for host in self.initial_hosts:
            scan = Scan(host, self.environment_state_service.network.get_all_subnets())
            await self.high_level_action_orchestrator.run_action(scan)

        # Initial access
        paths = []
        for host in self.initial_hosts:
            new_paths = self.attack_graph_service.get_possible_targets_from_host(host)
            paths.extend(new_paths)

        for attack_path in paths:
            if not self.attack_graph_service.already_executed_attack_path(attack_path):
                events = await self.high_level_action_orchestrator.run_action(
                    AttackPathLateralMove(attack_path)
                )
                if any_events_are_type(events, InfectedNewHost):
                    break

        webserver_host = None
        for host in self.environment_state_service.network.get_all_hosts():
            if host.hostname is None:
                continue

            if "webserver" in host.hostname:
                webserver_host = host

        if webserver_host is None:
            raise Exception("Webserver not found")

        events = await self.high_level_action_orchestrator.run_action(
            EscelatePrivledge(webserver_host)
        )
        print("Escalated privledge:")
        for event in events:
            print(event)

        events = await self.high_level_action_orchestrator.run_action(
            FindInformationOnAHost(webserver_host)
        )

        db_ip = None
        for event in events:
            if isinstance(event, SSHCredentialFound):
                db_ip = event.credential.host_ip
        if db_ip is None:
            raise Exception("Database cred not found")

        db_host = self.environment_state_service.network.find_host_by_ip(db_ip)
        if db_host is None:
            raise Exception("Database host not found")
        await self.high_level_action_orchestrator.run_action(
            LateralMoveToHost(db_host, webserver_host)
        )
        await self.high_level_action_orchestrator.run_action(
            FindInformationOnAHost(db_host)
        )
        await self.high_level_action_orchestrator.run_action(ExfiltrateData(db_host))

        return True
