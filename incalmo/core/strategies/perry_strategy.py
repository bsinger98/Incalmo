from incalmo.core.services import (
    EnvironmentStateService,
    AttackGraphService,
    LowLevelActionOrchestrator,
    HighLevelActionOrchestrator,
    ConfigService,
    PerryLogger,
)
from incalmo.api.server_api import C2ApiClient
from abc import ABC, abstractmethod
from datetime import datetime


class PerryStrategy(ABC):
    def __init__(
        self,
        logger: str = "perry",
    ):
        # Load config
        self.config = ConfigService().get_config()
        self.c2_client = C2ApiClient()

        # Services
        self.environment_state_service: EnvironmentStateService = (
            EnvironmentStateService(self.c2_client, self.config)
        )
        self.attack_graph_service: AttackGraphService = AttackGraphService(
            self.environment_state_service
        )
        self.logging_service: PerryLogger = PerryLogger(
            datetime.now().strftime("%Y%m%d_%H%M%S")
        ).setup_logger(logger)
        # Orchestrators
        self.low_level_action_orchestrator = LowLevelActionOrchestrator()

        self.high_level_action_orchestrator = HighLevelActionOrchestrator(
            self.environment_state_service,
            self.attack_graph_service,
            self.low_level_action_orchestrator,
        )

    async def initialize(self):
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

        return await self.step()

    @abstractmethod
    async def step(self) -> bool:
        pass
