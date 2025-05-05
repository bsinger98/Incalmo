import random

from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService
from plugins.deception.app.helpers.logging import get_logger, log_event

from plugins.deception.app.actions.HighLevel import (
    FindInformationOnAHost,
    AttackPathLateralMove,
    LateralMoveToHost,
    Scan,
    ExfiltrateData,
    EscelatePrivledge,
)
from plugins.deception.app.models.network import Host
from plugins.deception.app.strategies.perry_strategy import PerryStrategy
from plugins.deception.app.models.events import InfectedNewHost
from plugins.deception.app.strategies.util.event_util import any_events_are_type

from enum import Enum

plugin_logger = get_logger()


class DarksideState(Enum):
    InitialAccess = 0
    InfectNetwork = 1
    CompleteMission = 2
    Finished = 3


class LogicalPlanner(PerryStrategy):
    def __init__(
        self,
        operation: Operation,
        planning_svc: PlanningService,
        stopping_conditions=(),
    ):
        super().__init__(operation, planning_svc, stopping_conditions)

        self.state = DarksideState.InitialAccess
        self.hosts_explored: list[Host] = []

    async def step(self) -> bool:
        match self.state:
            case DarksideState.InitialAccess:
                await self.initial_access()
            case DarksideState.InfectNetwork:
                await self.infect_network()
            case DarksideState.CompleteMission:
                await self.complete_mission()
            case DarksideState.Finished:
                return True

        return False

    async def initial_access(self):
        for host in self.initial_hosts:
            self.hosts_explored.append(host)
            scan = Scan(host, self.environment_state_service.network.get_all_subnets())
            await self.high_level_action_orchestrator.run_action(scan)

        # Add initial paths to queue
        paths = []
        for host in self.initial_hosts:
            new_paths = self.attack_graph_service.get_possible_targets_from_host(host)
            paths.extend(new_paths)

        random.shuffle(paths)
        for path in paths:
            events = await self.high_level_action_orchestrator.run_action(
                AttackPathLateralMove(path, skip_if_already_executed=True)
            )

            if any_events_are_type(events, InfectedNewHost):
                self.state = DarksideState.InfectNetwork
                return

        # Unable to get initial access
        self.state = DarksideState.Finished

    async def infect_network(self):
        host_to_explore = None
        for host in self.environment_state_service.get_hosts_with_agents():
            if host not in self.hosts_explored:
                host_to_explore = host
                break

        # If no more hosts to explore, finish the mission
        if host_to_explore is None:
            self.state = DarksideState.CompleteMission
            return

        # Explore host 1) Escelate privledge, 2) Internal recon, 3) Lateral move
        self.hosts_explored.append(host_to_explore)
        # Escelate privledge
        await self.high_level_action_orchestrator.run_action(
            EscelatePrivledge(host_to_explore)
        )

        # Internal recon
        await self.high_level_action_orchestrator.run_action(
            FindInformationOnAHost(host_to_explore)
        )

        # Lateral move
        uninfected_hosts = self.environment_state_service.get_hosts_without_agents()
        random.shuffle(uninfected_hosts)
        for uninfected_host in uninfected_hosts:
            await self.high_level_action_orchestrator.run_action(
                LateralMoveToHost(uninfected_host, host_to_explore)
            )

    async def complete_mission(self):
        infected_hosts = self.environment_state_service.get_hosts_with_agents()
        for host in infected_hosts:
            if len(host.critical_data_files) > 0:
                # Exfiltrate data
                await self.high_level_action_orchestrator.run_action(
                    ExfiltrateData(host)
                )

        self.state = DarksideState.Finished
