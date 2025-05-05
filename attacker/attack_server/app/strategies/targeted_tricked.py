import random

from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService
from app.objects.c_agent import Agent

from plugins.deception.app.strategies.perry_strategy import PerryStrategy
from plugins.deception.app.actions.HighLevel import (
    Scan,
    AttackPathLateralMove,
    FindInformationOnAHost,
    ExfiltrateData,
)
from plugins.deception.app.models.network import AttackPath

from plugins.deception.app.helpers.logging import get_logger, log_event
from enum import Enum

plugin_logger = get_logger()


class AgentState(Enum):
    FIND_HOST_INFORMATION = 0
    SCAN = 1
    LATERAL_MOVE = 2
    FINISHED = 3


class RandomState(Enum):
    InitialAccess = 0
    RandomSpread = 1
    Finished = 2


class LogicalPlanner(PerryStrategy):
    def __init__(
        self,
        operation: Operation,
        planning_svc: PlanningService,
        stopping_conditions=(),
    ):
        super().__init__(operation, planning_svc, stopping_conditions)

        self.trusted_agents: list[Agent] = []
        self.state = RandomState.InitialAccess

        # agent paw -> state
        self.agent_states: dict[str, AgentState] = {}
        self.agent_attack_paths: dict[str, list[AttackPath]] = {}
        self.attack_path_queue: list[AttackPath] = []

        self.criticalHostKeyWords = [
            "decoy",
        ]

    def is_critical_host(self, hostname: str | None) -> bool:
        if hostname is None:
            return False

        for critical_host_name in self.criticalHostKeyWords:
            if critical_host_name in hostname.lower():
                return True

        return False

    async def step(self) -> bool:
        # Check if any new agents were created
        self.update_agent_states()

        if self.state == RandomState.InitialAccess:
            await self.initial_access()
        elif self.state == RandomState.RandomSpread:
            await self.random_spread()
        elif self.state == RandomState.Finished:
            return True
        return False

    def update_agent_states(self):
        initial_host_agent_paws = []
        for host in self.initial_hosts:
            agent_paws = [agent.paw for agent in host.agents]
            initial_host_agent_paws.extend(agent_paws)

        for agent in self.trusted_agents:
            if (
                agent.paw not in self.agent_states
                and agent.paw not in initial_host_agent_paws
            ):
                self.agent_states[agent.paw] = AgentState.FIND_HOST_INFORMATION

    async def initial_access(self):
        attacker_host = self.initial_hosts[0]

        scan = Scan(
            attacker_host, self.environment_state_service.network.get_all_subnets()
        )
        await self.high_level_action_orchestrator.run_action(scan)

        # Add initial paths to queue
        new_paths = self.attack_graph_service.get_possible_targets_from_host(
            attacker_host
        )
        random.shuffle(new_paths)
        self.attack_path_queue.extend(new_paths)
        self.state = RandomState.RandomSpread

    def choose_attack_path(self):
        chosen_attack_path = None
        # Prioritize attack paths with credentials to critical hosts
        for attack_path in self.attack_path_queue:
            if self.is_critical_host(attack_path.target_host.hostname):
                # fmt: off
                log_event("Choose attack path", f"Prioritizing: {attack_path.target_host.hostname}")
                # fmt: on

                chosen_attack_path = attack_path
                break
            if attack_path.attack_technique.CredentialToUse is not None:
                path_hostname = attack_path.attack_technique.CredentialToUse.hostname
                if self.is_critical_host(path_hostname):
                    # fmt: off
                    log_event('Choose attack path', f'Prioritizing cred for: {path_hostname}')
                    # fmt: on
                    chosen_attack_path = attack_path
                    break

        if chosen_attack_path is None:
            chosen_attack_path = self.attack_path_queue.pop(0)
        else:
            self.attack_path_queue.remove(chosen_attack_path)

        return chosen_attack_path

    async def random_spread(self):
        if self.all_agents_finished() and len(self.attack_path_queue) == 0:
            self.state = RandomState.Finished
            return

        for agent_paw, agent_state in self.agent_states.items():
            agent = self.get_agent_by_paw(agent_paw)
            if agent is None:
                continue

        # Execute last attack path in queue
        if len(self.attack_path_queue) > 0:
            attack_path = self.choose_attack_path()
            if not self.attack_graph_service.already_executed_attack_path(attack_path):
                await self.high_level_action_orchestrator.run_action(
                    AttackPathLateralMove(attack_path)
                )

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
                await self.high_level_action_orchestrator.run_action(
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
                # Add paths at end of queue (BFS)
                self.attack_path_queue = self.attack_path_queue + new_paths
                self.agent_states[agent_paw] = AgentState.FINISHED

        return

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
