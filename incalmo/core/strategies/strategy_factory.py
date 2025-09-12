import importlib
import inspect
from pathlib import Path
from incalmo.core.strategies.incalmo_strategy import IncalmoStrategy
from config.attacker_config import (
    AttackerConfig,
    LLMStrategyConfig,
    StateMachineStrategy,
)
from incalmo.core.strategies.llm.langchain_strategy import LangChainStrategy


class StrategyFactory:
    def __init__(self):
        self.strategies = {}
        self._register_state_machine_strategies()

    def register_strategy(self, name: str, strategy: type["IncalmoStrategy"]):
        """Manually register a strategy with a given name"""
        self.strategies[name] = strategy

    def get_strategy(self, name: str) -> type["IncalmoStrategy"]:
        """Get a registered strategy by name"""
        if name not in self.strategies:
            raise ValueError(
                f"Strategy '{name}' not found. Available strategies: {list(self.strategies.keys())}"
            )
        return self.strategies[name]

    def _register_state_machine_strategies(self):
        """Register all state machine strategies"""
        # Simple approach: just import the modules and let the classes register themselves
        # via a class attribute or we scan for IncalmoStrategy subclasses

        full_module_name = f"incalmo.core.strategies.state_machine.{module_name}"
        module = importlib.import_module(full_module_name)

        # Find all IncalmoStrategy subclasses in this module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, IncalmoStrategy)
                and obj != IncalmoStrategy
                and obj.__module__ == full_module_name
            ):
                self.strategies[name] = obj

    def list_available_strategies(self) -> list[str]:
        """Return a list of all registered strategy names"""
        return list(self.strategies.keys())

    def build_strategy(
        self, name: str, config: AttackerConfig, task_id: str = ""
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
