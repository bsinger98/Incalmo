from incalmo.core.strategies.incalmo_strategy import IncalmoStrategy
from incalmo.core.strategies.strategy_registry import STRATEGY_REGISTRY
from config.attacker_config import (
    AttackerConfig,
    LLMStrategyConfig,
    StateMachineStrategy,
)
from incalmo.core.strategies.llm.langchain_strategy import LangChainStrategy
import incalmo.core.strategies


class StrategyFactory:
    def __init__(self):
        # Use the global strategy registry
        self.registry = STRATEGY_REGISTRY
        # Discover and register all strategies in the strategies package
        self.registry.discover(incalmo.core.strategies)

    def register_strategy(self, name: str, strategy: type["IncalmoStrategy"]):
        """Manually register a strategy with a given name"""
        self.registry.register(strategy, name=name)

    def get_strategy(self, name: str) -> type["IncalmoStrategy"]:
        """Get a registered strategy by name"""
        return self.registry.get(name)

    def list_available_strategies(self) -> list[str]:
        """Return a list of all registered strategy names"""
        return self.registry.list_strategies()

    def build_strategy(
        self, config: AttackerConfig, task_id: str = ""
    ) -> IncalmoStrategy:
        """Build and return a strategy instance based on the config"""
        if isinstance(config.strategy, LLMStrategyConfig):
            return LangChainStrategy(config=config, task_id=task_id)
        elif isinstance(config.strategy, StateMachineStrategy):
            strategy_name = config.strategy.name
            strategy_class = self.get_strategy(strategy_name)
            return strategy_class(config=config, task_id=task_id)
        else:
            raise ValueError(f"Unknown strategy type: {type(config.strategy)}")
