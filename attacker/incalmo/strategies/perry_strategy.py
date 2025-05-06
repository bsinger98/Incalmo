import asyncio

from helpers.logging import (
    PerryLogger,
    init_logger,
)

from actions.HighLevel import *
from actions.LowLevel import MD5SumAttackerData
from models.network import *
from models.events import *

from services import (
    EnvironmentStateService,
    AttackGraphService,
    LowLevelActionOrchestrator,
    HighLevelActionOrchestrator,
    ConfigService,
)

from enum import Enum
from abc import ABC, abstractmethod
import json

# Mutex to prevent multiple strategies from running at the same time
strategy_mutex: bool = False


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class PerryStrategy(ABC):
    def __init__(
        self,
        stopping_conditions=(),
    ):
        self.stopping_conditions = stopping_conditions
        self.stopping_condition_met = False

        self.trusted_agents: list[Agent] = []
        self.initial_hosts: list[Host] = []
        self.state = EquifaxAttackerState.InitialAccess
        self.new_initial_access_agent: Agent | None = None
        self.new_initial_access_host: Host | None = None
        self.external_subnet = None

        # Setup logging
        self.log_creator = PerryLogger(self.operation.id)
        self.perry_logger = self.log_creator.setup_logger("perry")
        self.perry_logger.info("Perry logger initialized")
        init_logger(self.log_creator.logger_dir_path)

        # Load config
        self.config = ConfigService().get_config()

        # Services
        self.environment_state_service: EnvironmentStateService = (
            EnvironmentStateService(self.knowledge_svc_handle, operation, self.config)
        )
        self.attack_graph_service: AttackGraphService = AttackGraphService(
            self.environment_state_service
        )
        # Orchestrators
        self.low_level_action_orchestrator = LowLevelActionOrchestrator(
            self.operation,
            self.planning_svc,
            self.knowledge_svc_handle,
            self.environment_state_service,
        )
        self.high_level_action_orchestrator = HighLevelActionOrchestrator(
            self.environment_state_service,
            self.attack_graph_service,
            self.low_level_action_orchestrator,
        )

        # States
        self.state_machine = ["main", "spin_loop"]
        # Agents go from try to read flag -> scan -> randomly laterally move -> finished
        self.agent_states = {}

        # Bug in Caldera can launch multiple strategies at the same time
        global strategy_mutex
        if strategy_mutex:
            self.next_bucket = "spin_loop"
        else:
            strategy_mutex = True
            self.next_bucket = "main"

    async def initialize(self):
        # Create exploits.py if it does not exist
        with open("plugins/deception/payloads/exploit.py", "w") as exploit_file:
            exploit_file.write("")

        self.update_trusted_agents()
        if len(self.trusted_agents) == 0:
            self.perry_logger.error("No trusted agents found")
            raise Exception("No trusted agents found")

        self.environment_state_service.update_host_agents(self.trusted_agents)
        self.initial_hosts = self.environment_state_service.get_hosts_with_agents()
        self.environment_state_service.set_initial_hosts(self.initial_hosts)

    def update_trusted_agents(self):
        self.trusted_agents = list(
            filter(lambda agent: agent.trusted, self.operation.agents)
        )

    async def execute(self):
        self.perry_logger.info("Executing strategy...")
        self.update_trusted_agents()

        await self.initialize()
        await self.planning_svc.execute_planner(self)

    def cleanup(self):
        experiment_log_dir = self.log_creator.logger_dir_path

        with open(f"{experiment_log_dir}/high_level_action.json", "w") as f:
            f.write(
                json.dumps(self.high_level_action_orchestrator.high_level_action_log)
            )

        with open(f"{experiment_log_dir}/low_level_action.json", "w") as f:
            f.write(json.dumps(self.low_level_action_orchestrator.low_level_action_log))

    async def main(self):
        # Check if any new agents were created
        self.update_trusted_agents()
        self.environment_state_service.update_host_agents(self.trusted_agents)

        finished = await self.step()

        if finished:
            global strategy_mutex
            strategy_mutex = False
            self.cleanup()
            self.state = EquifaxAttackerState.Finished
            self.stopping_condition_met = True
            self.next_bucket = None
            return

        self.next_bucket = "main"

    async def spin_loop(self):
        global strategy_mutex

        if strategy_mutex:
            await asyncio.sleep(5)
            return
        else:
            self.stopping_condition_met = True
            self.next_bucket = None

    @abstractmethod
    async def step(self) -> bool:
        pass
