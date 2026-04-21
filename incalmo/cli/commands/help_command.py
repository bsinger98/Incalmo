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
            "discover": "Perform discovery operations. Format: /discover <host_ip>",
            "move": "Perform lateral movement operations. Format: /move <source_host_ip> <target_host_ip>",
            "privesc": "Perform privilege escalation operations. Format: /privesc <host_ip>",
            "exfil": "Exfiltrate data from compromised hosts. Format: /exfil <host_ip>",
            "exit": "Exit the REPL",
        }

        # Build the base help text
        help_parts = [
            ("Incalmo Help", "bold white"),
            ("\n\n", ""),
            ("Send instructions (without /) to send to the LLM for analysis\n\n", "green"),
            ("Send specific requests with the following commands\n\n", "green"),
        ]

        # Add commands dynamically
        for cmd, desc in commands.items():
            help_parts.extend(
                [("🔹 ", "cyan"), (f"/{cmd}", "cyan"), (f" - {desc}\n", "dim white")]
            )

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
