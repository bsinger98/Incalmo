from incalmo.core.services import (
    EnvironmentStateService,
    AttackGraphService,
    LowLevelActionOrchestrator,
    HighLevelActionOrchestrator,
    IncalmoLogger,
)
from config.attacker_config import AttackerConfig
from incalmo.api.server_api import C2ApiClient
from abc import ABC, abstractmethod
from datetime import datetime


class IncalmoStrategy(ABC):
    """Base strategy class that auto-registers subclasses."""

    def __init_subclass__(
        cls, *, name: str | None = None, register: bool = True, **kwargs
    ):
        """Inherit from this to auto-register subclasses."""
        super().__init_subclass__(**kwargs)
        if register:
            # Import here to avoid circular imports
            from incalmo.core.strategies.strategy_registry import STRATEGY_REGISTRY

            STRATEGY_REGISTRY.register(cls, name=name)

    def __init__(
        self,
        config: AttackerConfig,
        logger: str = "incalmo",
        task_id: str = "",
    ):
        # Load config
        self.config = config
        self.c2_client = C2ApiClient()
        self.task_id = task_id

        # Services
        self.environment_state_service: EnvironmentStateService = (
            EnvironmentStateService(self.c2_client, self.config)
        )
        self.attack_graph_service: AttackGraphService = AttackGraphService(
            self.environment_state_service
        )
        self.logging_service: IncalmoLogger = IncalmoLogger(
            operation_id=f"{self.config.name}_{task_id}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        )
        # Orchestrators
        self.low_level_action_orchestrator = LowLevelActionOrchestrator(
            self.logging_service,
        )

        self.high_level_action_orchestrator = HighLevelActionOrchestrator(
            self.environment_state_service,
            self.attack_graph_service,
            self.low_level_action_orchestrator,
            self.logging_service,
        )

    @classmethod
    def initialize_base_environment(cls, config: AttackerConfig):
        """Initialize base environment and return initial hosts without running strategy"""
        c2_client = C2ApiClient()
        env_service = EnvironmentStateService(c2_client, config)

        agents = c2_client.get_agents()
        env_service.update_host_agents(agents)
        c2_client.report_environment_state(env_service.network)

    async def initialize(self, task_id: str = ""):
        agents = self.c2_client.get_agents()
        if len(agents) == 0:
            raise Exception("No trusted agents found")
        self.environment_state_service.update_host_agents(agents)
        self.initial_hosts = self.environment_state_service.get_hosts_with_agents()
        self.environment_state_service.set_initial_hosts(self.initial_hosts)

    async def main(self) -> bool:
        # Check if any new agents were created
        agents = self.c2_client.get_agents()
        self.environment_state_service.update_host_agents(agents)
        self.c2_client.report_environment_state(self.environment_state_service.network)
        print(f"[DEBUG] Current environment state: {self.environment_state_service}")
        return await self.step()

    @abstractmethod
    async def step(self) -> bool:
        pass
