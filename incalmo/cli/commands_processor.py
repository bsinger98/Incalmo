#!/usr/bin/env python3
"""
Command processing and handling for Incalmo CLI REPL
"""

from rich.text import Text
from textual.widgets import RichLog
from typing import TYPE_CHECKING, Dict

from incalmo.cli.commands import load_commands, BaseCommand

if TYPE_CHECKING:
    from incalmo.cli.session import SessionManager


class CommandRegistry:
    """Registry for managing CLI commands in a scalable way."""

    def __init__(self, session_manager: "SessionManager"):
        self._commands: Dict[str, BaseCommand] = {}
        self._aliases: Dict[str, str] = {}
        self._load_commands(session_manager)

    def _load_commands(self, session_manager: "SessionManager"):
        """Load all commands from the commands package."""
        commands = load_commands(session_manager)

        for command in commands:
            self.register_command(command)

    def register_command(self, command: BaseCommand):
        """Register a command instance."""
        self._commands[command.name] = command

        # Register aliases
        for alias in command.aliases:
            self._aliases[alias] = command.name

    def get_command(self, name: str) -> BaseCommand | None:
        """Get command instance by name or alias."""
        # Check if it's an alias first
        if name in self._aliases:
            name = self._aliases[name]

        return self._commands.get(name)

    def get_commands(self) -> Dict[str, str]:
        """Get all registered commands with their descriptions."""
        return {name: cmd.description for name, cmd in self._commands.items()}

    def has_command(self, name: str) -> bool:
        """Check if a command exists."""
        return name in self._commands or name in self._aliases


class CommandProcessor:
    """Handles command processing and execution."""

    def __init__(self, session_manager: "SessionManager"):
        self.session = session_manager
        self.registry = CommandRegistry(session_manager)

    def process_command(self, command: str, output: RichLog) -> str | None:
        """Process input - either a slash command or paragraph text."""
        # Check if this is a slash command
        if command.startswith("/"):
            return self.process_slash_command(
                command[1:], output
            )  # Remove the leading slash
        else:
            # Handle as paragraph text
            self.process_paragraph_text(command, output)
            return None

    def process_slash_command(self, command: str, output: RichLog) -> str | None:
        """Process a slash command."""
        parts = command.split(None, 1)
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Get command from registry
        command_obj = self.registry.get_command(cmd)
        if command_obj:
            return command_obj.execute(args, output)
        else:
            self.handle_unknown_command(cmd, output)

    def process_paragraph_text(self, text: str, output: RichLog) -> None:
        """Process paragraph text input."""
        # Display the paragraph text with a different styling
        paragraph_text = Text.assemble(
            ("📝 ", "blue"),
            ("Text received: ", "dim white"),
            ("\n", ""),
            (text, "white"),
        )
        output.write(paragraph_text)

        # Add a note about slash commands if this looks like it might have been intended as a command
        if any(word in text.lower() for word in ["help", "discover", "scan", "find"]):
            hint_text = Text.assemble(
                ("💡 ", "dim yellow"),
                ("Tip: Use ", "dim white"),
                ("/command", "cyan"),
                (" format for commands (e.g., ", "dim white"),
                ("/discover please look at this host", "cyan"),
                (")", "dim white"),
            )
            output.write(hint_text)

    def handle_unknown_command(self, cmd: str, output: RichLog) -> None:
        """Handle unknown commands."""
        error_text = Text.assemble(
            ("❌ ", "red"), ("Unknown slash command: /", "red"), (cmd, "bold red")
        )
        output.write(error_text)
        help_text = Text.assemble(
            ("💡 Type ", "dim white"),
            ("/help", "cyan"),
            (" to see available commands", "dim white"),
        )
        output.write(help_text)

    def get_available_commands(self):
        """Get list of available commands for filtering."""
        commands = self.registry.get_commands()
        return [(cmd, desc) for cmd, desc in commands.items()]
