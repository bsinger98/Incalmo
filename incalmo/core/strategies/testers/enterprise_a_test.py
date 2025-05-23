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
        webserver_subnet = (
            self.environment_state_service.network.find_subnet_by_ip_mask(
                "192.168.200.0/24"
            )
        )

        for host in self.initial_hosts:
            scan = Scan(host, [webserver_subnet])
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
            raise Exception("Webserver not infected")

        database_subnet = self.environment_state_service.network.find_subnet_by_ip_mask(
            "192.168.203.0/24"
        )
        events = await self.high_level_action_orchestrator.run_action(
            Scan(webserver_host, [database_subnet])
        )

        management_host = None
        for host in self.environment_state_service.network.get_all_hosts():
            if host.open_ports.get(4444) is not None:
                management_host = host
                break

        if management_host is None:
            raise Exception("Management host not found")

        await self.high_level_action_orchestrator.run_action(
            LateralMoveToHost(management_host, webserver_host)
        )
        await self.high_level_action_orchestrator.run_action(
            FindInformationOnAHost(management_host)
        )

        paths = self.attack_graph_service.get_possible_targets_from_host(
            management_host
        )
        db_path = None
        for path in paths:
            if path.attack_technique.CredentialToUse is not None:
                db_path = path
                break

        if db_path is None:
            raise Exception("Database path not found")

        events = await self.high_level_action_orchestrator.run_action(
            AttackPathLateralMove(db_path)
        )

        db_host = db_path.target_host
        await self.high_level_action_orchestrator.run_action(
            FindInformationOnAHost(db_host)
        )
        await self.high_level_action_orchestrator.run_action(ExfiltrateData(db_host))

        return True
