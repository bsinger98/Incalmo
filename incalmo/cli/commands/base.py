#!/usr/bin/env python3
"""
Base command class for Incalmo CLI commands
"""

from abc import ABC, abstractmethod
from rich.text import Text
from textual.widgets import RichLog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..session import SessionManager


class BaseCommand(ABC):
    """Base class for all CLI commands."""

    def __init__(self, session_manager: "SessionManager"):
        self.session = session_manager

    @property
    @abstractmethod
    def name(self) -> str:
        """The command name (without the leading slash)."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A brief description of what the command does."""
        pass

    @property
    def aliases(self) -> list[str]:
        """Alternative names for this command. Override if needed."""
        return []

    @abstractmethod
    def execute(self, args: str, output: RichLog) -> str | None:
        """
        Execute the command with the given arguments.

        Args:
            args: The arguments passed to the command
            output: The RichLog widget to write output to

        Returns:
            Optional string for special actions (e.g., "exit" to quit the REPL)
        """
        pass

    def get_usage(self) -> str:
        """Get usage information for this command. Override if needed."""
        return f"/{self.name}"

    def get_help_text(self) -> str:
        """Get detailed help text for this command. Override if needed."""
        return self.description
