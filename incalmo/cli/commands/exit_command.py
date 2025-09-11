#!/usr/bin/env python3
"""
Exit command for Incalmo CLI
"""

from textual.widgets import RichLog

from incalmo.cli.commands.base import BaseCommand


class ExitCommand(BaseCommand):
    """Exit the REPL."""

    @property
    def name(self) -> str:
        return "exit"

    @property
    def description(self) -> str:
        return "Exit the REPL"

    @property
    def aliases(self) -> list[str]:
        return ["quit"]

    def execute(self, args: str, output: RichLog) -> str | None:
        """Execute the exit command."""
        return "exit"
