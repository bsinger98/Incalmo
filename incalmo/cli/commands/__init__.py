#!/usr/bin/env python3
"""
Commands package for Incalmo CLI
"""

import importlib
import inspect
import pkgutil
from typing import TYPE_CHECKING, Type, List

from incalmo.cli.commands.base import BaseCommand
from incalmo.cli.commands.llm_command_base import BaseLLMCommand
from incalmo.cli.commands.llm_agent_command_base import LLMAgentCommand

if TYPE_CHECKING:
    from incalmo.cli.session import SessionManager


def discover_commands() -> List[Type[BaseCommand]]:
    """
    Automatically discover all command classes in this package.

    Returns:
        List of command classes that inherit from BaseCommand
    """
    command_classes = []

    # Get the current package
    package = __import__(__name__, fromlist=[""])

    # Iterate through all modules in this package
    for importer, modname, ispkg in pkgutil.iter_modules(
        package.__path__, package.__name__ + "."
    ):
        if modname.endswith("_command"):  # Only load files ending with '_command'
            try:
                module = importlib.import_module(modname)

                # Find all classes in the module that inherit from BaseCommand
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                    obj != BaseCommand
                    and obj != BaseLLMCommand
                    and obj != LLMAgentCommand
                    and (issubclass(obj, BaseCommand) or issubclass(obj, BaseLLMCommand) or issubclass(obj, LLMAgentCommand))
                    and obj.__module__ == modname
                ):
                        command_classes.append(obj)

            except ImportError as e:
                print(f"Warning: Could not import command module {modname}: {e}")
                continue

    return command_classes


def load_commands(session_manager: "SessionManager") -> List[BaseCommand]:
    """
    Load and instantiate all discovered commands.

    Args:
        session_manager: The session manager to pass to command constructors

    Returns:
        List of instantiated command objects
    """
    command_classes = discover_commands()
    commands = []

    for command_class in command_classes:
        try:
            command_instance = command_class(session_manager)
            commands.append(command_instance)
        except Exception as e:
            print(
                f"Warning: Could not instantiate command {command_class.__name__}: {e}"
            )
            continue

    return commands


# Export the base class and discovery functions
__all__ = ["BaseCommand", "LLMAgentCommand", "discover_commands", "load_commands"]
