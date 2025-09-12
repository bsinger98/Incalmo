"""
Strategy Registry for automatically registering IncalmoStrategy subclasses.
"""

from typing import Dict, Type, List
import types
import pkgutil
import importlib


class StrategyRegistry:
    """A simple registry that stores IncalmoStrategy subclasses."""

    def __init__(self):
        self._strategies: Dict[str, Type] = {}

    def register(self, strategy_class: Type, *, name: str | None = None) -> None:
        """
        Register a strategy class.

        Args:
            strategy_class: The strategy class to register
            name: Optional name to register under. If None, uses class name.
        """
        registry_name = name or strategy_class.__name__
        self._strategies[registry_name] = strategy_class

    def get(self, name: str) -> Type:
        """
        Get a registered strategy class by name.

        Args:
            name: The name of the strategy to retrieve

        Returns:
            The strategy class

        Raises:
            KeyError: If the strategy name is not found
        """
        if name not in self._strategies:
            raise KeyError(
                f"Strategy '{name}' not found. Available strategies: {list(self._strategies.keys())}"
            )
        return self._strategies[name]

    def list_strategies(self) -> List[str]:
        """Return a list of all registered strategy names."""
        return list(self._strategies.keys())

    def get_all_strategies(self) -> Dict[str, Type]:
        """Return a dictionary of all registered strategies."""
        return self._strategies.copy()

    def __contains__(self, name: str) -> bool:
        """Check if a strategy is registered."""
        return name in self._strategies

    def __len__(self) -> int:
        """Return the number of registered strategies."""
        return len(self._strategies)

    def __repr__(self) -> str:
        """Return a string representation of the registry."""
        return f"StrategyRegistry({list(self._strategies.keys())})"

    def discover(self, package: types.ModuleType) -> None:
        """
        Import all submodules in a package so subclass definitions run,
        which triggers registration.
        """
        if not hasattr(package, "__path__"):
            return  # not a package
        prefix = package.__name__ + "."
        for modinfo in pkgutil.walk_packages(package.__path__, prefix):
            try:
                importlib.import_module(modinfo.name)
            except ImportError as e:
                # Log but don't fail - some modules might have missing dependencies
                print(f"Warning: Could not import {modinfo.name}: {e}")


# Global registry instance
STRATEGY_REGISTRY = StrategyRegistry()
