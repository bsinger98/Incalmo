from incalmo.core.services import (
    EnvironmentStateService,
    AttackGraphService,
    LowLevelActionOrchestrator,
    HighLevelActionOrchestrator,
    ConfigService,
    IncalmoLogger,
)
from incalmo.api.server_api import C2ApiClient
from abc import ABC, abstractmethod
from datetime import datetime


class IncalmoStrategy(ABC):
    _registry: dict[str, type["IncalmoStrategy"]] = {}

    def __init_subclass__(cls, *, name: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if name is None:
            name = cls.__name__.lower()
        cls._registry[name] = cls

    @classmethod
    def get(cls, name: str) -> type["IncalmoStrategy"]:
        print("Registered strategies:", IncalmoStrategy._registry.keys())
        try:
            print(f"Retrieving strategy: {name.lower()}")
            return cls._registry[name.lower()]
        except KeyError as e:
            raise ValueError(f"Unknown strategy '{name}'") from e

    @classmethod
    def build_strategy(cls, name: str, **kwargs) -> "IncalmoStrategy":
        strategy_cls = cls.get(name)
        print(f"Building strategy: {strategy_cls.__name__} with args: {kwargs}")
        return strategy_cls(**kwargs)

    def __init__(
        self,
        logger: str = "incalmo",
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
        self.logging_service: IncalmoLogger = IncalmoLogger(
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
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
