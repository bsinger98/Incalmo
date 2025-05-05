import random

from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService
from plugins.deception.app.helpers.logging import get_logger, log_event

from plugins.deception.app.actions.HighLevel import (
    FindInformationOnAHost,
    AttackPathLateralMove,
    Scan,
    ExfiltrateData,
)
from plugins.deception.app.models.network import AttackPath
from plugins.deception.app.models.events import InfectedNewHost
from plugins.deception.app.strategies.perry_strategy import PerryStrategy

from enum import Enum

plugin_logger = get_logger()


class AgentState(Enum):
    FIND_HOST_INFORMATION = 0
    SCAN = 1
    LATERAL_MOVE = 2
    FINISHED = 3


class GambitState(Enum):
    InitialAccess = 0
    ExploreNetwork = 1
    Finished = 2


class LogicalPlanner(PerryStrategy):
    def __init__(
        self,
        operation: Operation,
        planning_svc: PlanningService,
        stopping_conditions=(),
    ):
        super().__init__(operation, planning_svc, stopping_conditions)

        self.state = GambitState.InitialAccess
        # agent paw -> state
        self.agent_states: dict[str, AgentState] = {}
        self.agent_attack_paths: dict[str, list[AttackPath]] = {}
        self.attack_path_queue: list[AttackPath] = []
        self.initial_agents_paws = []

    def update_agent_states(self):
        for agent in self.trusted_agents:
            if (
                agent.paw not in self.agent_states
                and agent.paw not in self.initial_agents_paws
            ):
                self.agent_states[agent.paw] = AgentState.FIND_HOST_INFORMATION

        # Remove agents that are no longer in operation
        for agent_paw in list(self.agent_states.keys()):
            if agent_paw not in [agent.paw for agent in self.trusted_agents]:
                del self.agent_states[agent_paw]

    async def step(self) -> bool:
        # Check if any new agents were created
        self.update_agent_states()

        if self.state == GambitState.InitialAccess:
            await self.initial_access()
        elif self.state == GambitState.ExploreNetwork:
            await self.explore_network()
        elif self.state == GambitState.Finished:
            return True

        return False

    async def initial_access(self):
        for agent in self.trusted_agents:
            self.initial_agents_paws.append(agent.paw)

        for host in self.initial_hosts:
            scan = Scan(host, self.environment_state_service.network.get_all_subnets())
            await self.high_level_action_orchestrator.run_action(scan)

        # Add initial paths to queue
        paths = []
        for host in self.initial_hosts:
            new_paths = self.attack_graph_service.get_possible_targets_from_host(host)
            paths.extend(new_paths)

        random.shuffle(paths)
        self.attack_path_queue.extend(paths)

        self.state = GambitState.ExploreNetwork

    async def explore_network(self):
        log_event("Explore network", "Exploring network...")
        if self.all_agents_finished() and len(self.attack_path_queue) == 0:
            self.state = GambitState.Finished
            return

        for agent_paw, agent_state in self.agent_states.items():
            agent = self.get_agent_by_paw(agent_paw)
            if agent is None:
                continue

            if agent_state == AgentState.FIND_HOST_INFORMATION:
                host = self.environment_state_service.network.find_host_by_agent(agent)
                if host is None:
                    continue

                # New host created: 1) find information, 2) scan, 3) add attack paths to queue
                # Find information
                events = await self.high_level_action_orchestrator.run_action(
                    FindInformationOnAHost(host)
                )

                if len(host.critical_data_files) > 0:
                    await self.high_level_action_orchestrator.run_action(
                        ExfiltrateData(host)
                    )

                # Add attack paths to queue
                new_paths = self.attack_graph_service.get_possible_targets_from_host(
                    host
                )
                random.shuffle(new_paths)
                # Prepend new paths to queue
                self.attack_path_queue = new_paths + self.attack_path_queue
                self.agent_states[agent_paw] = AgentState.FINISHED

        if len(self.attack_path_queue) > 0:
            attack_path = self.attack_path_queue.pop()
            if not self.attack_graph_service.already_executed_attack_path(attack_path):
                # Check if host still infected
                if len(attack_path.attack_host.agents) > 0:
                    events = await self.high_level_action_orchestrator.run_action(
                        AttackPathLateralMove(attack_path)
                    )
                else:
                    # fmt: off
                    log_event('Explore network', f'Trying to reinfect: {attack_path.attack_host}')
                    # fmt: on

                    # Reinfect host, prioritize internal hosts
                    reinfect_paths = (
                        self.attack_graph_service.get_attack_paths_to_target(
                            attack_path.attack_host, prioritize_internal_hosts=True
                        )
                    )

                    for path in reinfect_paths:
                        events = await self.high_level_action_orchestrator.run_action(
                            AttackPathLateralMove(path)
                        )
                        for event in events:
                            if isinstance(event, InfectedNewHost):
                                log_event("Explore network", f"Reinfected host!")
                                # Add original path back to queue
                                self.attack_path_queue.append(attack_path)
                                break

    def get_agent_by_paw(self, paw: str):
        for agent in self.trusted_agents:
            if agent.paw == paw:
                return agent

        return None

    def all_agents_finished(self):
        for agent_paw, agent_state in self.agent_states.items():
            if agent_state != AgentState.FINISHED:
                return False

        return True
