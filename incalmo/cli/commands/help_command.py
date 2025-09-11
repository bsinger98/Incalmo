#!/usr/bin/env python3
"""
Help command for Incalmo CLI
"""

from rich.text import Text
from textual.widgets import RichLog

from incalmo.cli.commands.base import BaseCommand


class HelpCommand(BaseCommand):
    """Display help information about available commands."""

    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return "Show detailed help information"

    @property
    def aliases(self) -> list[str]:
        return ["?"]

    def execute(self, args: str, output: RichLog) -> str | None:
        """Execute the help command."""
        # We'll need to get the registry from somewhere - for now use a simple approach
        # In a more sophisticated setup, you might inject the registry or use a service locator
        commands = {
            "help": "Show detailed help information",
            "discover": "Perform discovery operations",
            "exit": "Exit the REPL",
        }

        # Build the base help text
        help_parts = [
            ("Incalmo Help", "bold white"),
            ("\n\n", ""),
            ("TODO: Add help text here", "green"),
        ]

        # Add commands dynamically
        # for cmd, desc in commands.items():
        #     help_parts.extend(
        #         [("🔹 ", "cyan"), (f"/{cmd}", "cyan"), (f" - {desc}\n", "dim white")]
        #     )

        # Add footer
        # help_parts.extend(
        #     [
        #         ("\n", ""),
        #         ("💡 ", "bold yellow"),
        #         ("Use ", "dim white"),
        #         ("/discover <request>", "cyan"),
        #         (" to perform discovery operations", "dim white"),
        #     ]
        # )

        help_text = Text.assemble(*help_parts)
        output.write(help_text)

        return None
