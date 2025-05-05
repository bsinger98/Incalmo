import random
import asyncio

from app.utility.base_service import BaseService
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService
from app.service.knowledge_svc import KnowledgeService
from app.objects.c_agent import Agent

from .helpers.logging import get_logger, setup_logger_for_operation, log_event
from .helpers.agent_helpers import find_attacker_agent

from .actions.HighLevel import (
    DiscoverHostInformation,
    LateralMoveToHost,
    AttackPathLateralMove,
    Scan,
    SmartExfiltrateData,
)
from .actions.Information import Host, Subnet, Network, AttackPath
from .actions.Information.KnowledgeBase import KnowledgeBase
from .actions.Events import InfectedNewHost

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


class LogicalPlanner:
    def __init__(
        self,
        operation: Operation,
        planning_svc: PlanningService,
        stopping_conditions=(),
    ):
        self.operation = operation
        self.planning_svc = planning_svc
        self.stopping_conditions = stopping_conditions
        self.stopping_condition_met = False
        self.knowledge_svc_handle: KnowledgeService = BaseService.get_service(
            "knowledge_svc"
        )

        self.trusted_agents: list[Agent] = []
        self.attacker_agent: Agent
        self.state = GambitState.InitialAccess
        self.peristant_hosts: list[Host] = []
        self.peristant_attack_paths: list[AttackPath] = []
        # agent paw -> state
        self.agent_states: dict[str, AgentState] = {}
        self.agent_attack_paths: dict[str, list[AttackPath]] = {}
        self.attack_path_queue: list[AttackPath] = []

        # Setup logger
        setup_logger_for_operation(self.operation.id)
        plugin_logger.info(f"* NEW OPERATION STARTED at {self.operation.start}")

        network = Network([Subnet("192.168.200.0/24"), Subnet("192.168.201.0/24")])
        self.knowledge_base = KnowledgeBase(
            network, self.knowledge_svc_handle, operation
        )

        # Setup actions
        self.scanAction = Scan(
            self.operation, self.planning_svc, self.knowledge_svc_handle
        )
        self.discoverInfoAction = DiscoverHostInformation(
            self.operation, self.planning_svc, self.knowledge_svc_handle
        )
        self.infectHostAction = LateralMoveToHost(
            self.operation, self.planning_svc, self.knowledge_svc_handle
        )
        self.attackPathInfect = AttackPathLateralMove(
            self.operation, self.planning_svc, self.knowledge_svc_handle
        )
        self.exfiltrateDataAction = SmartExfiltrateData(
            self.operation, self.planning_svc, self.knowledge_svc_handle
        )

        # States
        self.state_machine = ["main"]
        # Agents go from try to read flag -> scan -> randomly laterally move -> finished
        self.agent_states = {}
        self.pawn_host = None

        self.next_bucket = "main"

    def update_trusted_agents(self):
        self.trusted_agents = list(
            filter(lambda agent: agent.trusted, self.operation.agents)
        )

    async def initialize(self):
        attacker_agent = await find_attacker_agent(self.operation)
        if attacker_agent is None:
            log_event("Initialization", "ERROR agent not found")
            self.state = GambitState.Finished
            return
        else:
            self.attacker_agent = attacker_agent

        attackerSubnet = Subnet("192.168.202.0/24", attacker_subnet=True)
        attacker_ip = self.attacker_agent.host_ip_addrs[0]
        self.attacker_host = Host(hostname="attacker", ip_address=attacker_ip)
        attackerSubnet.add_host(self.attacker_host)
        self.knowledge_base.network.add_subnet(attackerSubnet)

    async def execute(self):
        log_event("EXECUTE", "Executing logical planner")
        self.update_trusted_agents()
        await self.initialize()
        await self.planning_svc.execute_planner(self)

    async def main(self):
        # Check if any new agents were created
        self.update_trusted_agents()
        self.update_agent_states()
        self.knowledge_base.update_host_agents(self.trusted_agents)

        if self.state == GambitState.InitialAccess:
            await self.initial_access()
        elif self.state == GambitState.ExploreNetwork:
            await self.explore_network()
        elif self.state == GambitState.Finished:
            self.stopping_condition_met = True
            self.next_bucket = None
            return

        self.next_bucket = "main"
        return

    def update_agent_states(self):
        for agent in self.trusted_agents:
            if (
                agent.paw not in self.agent_states
                and agent.paw != self.attacker_agent.paw
            ):
                self.agent_states[agent.paw] = AgentState.FIND_HOST_INFORMATION

        # Remove agents that are no longer in operation
        for agent_paw in list(self.agent_states.keys()):
            if agent_paw not in [agent.paw for agent in self.trusted_agents]:
                del self.agent_states[agent_paw]

    async def initial_access(self):
        # Use attacker host to scan external network
        events = await self.scanAction.run(
            self.attacker_agent, self.knowledge_base.network.get_all_subnets()
        )
        self.knowledge_base.parse_events(events)

        # Add initial paths to queue
        new_paths = self.knowledge_base.network.get_possible_targets_from_host(
            self.attacker_host
        )
        random.shuffle(new_paths)
        self.attack_path_queue.extend(new_paths)

        self.state = GambitState.ExploreNetwork

    async def explore_network(self):
        log_event("Explore network", "Exploring network...")
        if self.all_agents_finished() and len(self.attack_path_queue) == 0:
            log_event("Explore network", "Finished")
            self.state = GambitState.Finished
            return

        for agent_paw, agent_state in self.agent_states.items():
            agent = self.get_agent_by_paw(agent_paw)
            if agent is None:
                continue

            if agent_state == AgentState.FIND_HOST_INFORMATION:
                host = self.knowledge_base.network.find_host_by_agent(agent)
                if host is None:
                    continue

                # New host created: 1) find information, 2) scan, 3) add attack paths to queue
                # Find information
                events = await self.discoverInfoAction.run(agent, host)
                self.knowledge_base.parse_events(events)

                events = await self.exfiltrateDataAction.run(
                    self.attacker_agent, host, self.knowledge_base.network
                )
                self.knowledge_base.parse_events(events)

                # Add attack paths to queue
                new_paths = self.knowledge_base.network.get_possible_targets_from_host(
                    host
                )
                random.shuffle(new_paths)
                # Prepend new paths to queue
                self.attack_path_queue = new_paths + self.attack_path_queue
                random.shuffle(self.attack_path_queue)
                self.agent_states[agent_paw] = AgentState.FINISHED

        if len(self.attack_path_queue) > 0:
            # Pop random attack path from queue
            attack_path = self.attack_path_queue.pop()

            if not self.knowledge_base.already_executed_attack_path(attack_path):
                # Check if host still infected
                if len(attack_path.attack_host.agents) > 0:
                    events = await self.attackPathInfect.run(attack_path)
                    self.knowledge_base.executed_attack_path(attack_path)
                    self.knowledge_base.parse_events(events)
                else:
                    # fmt: off
                    log_event('Explore network', f'Trying to reinfect: {attack_path.attack_host}')
                    # fmt: on

                    # Reinfect host, prioritize internal hosts
                    reinfect_paths = (
                        self.knowledge_base.network.get_attack_paths_to_target(
                            attack_path.attack_host, prioritize_internal_hosts=True
                        )
                    )

                    for path in reinfect_paths:
                        events = await self.attackPathInfect.run(path)
                        self.knowledge_base.parse_events(events)
                        for event in events:
                            if isinstance(event, InfectedNewHost):
                                log_event("Explore network", f"Reinfected host!")
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
