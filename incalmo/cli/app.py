#!/usr/bin/env python3
"""
Core Incalmo CLI REPL Application
"""

from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Input, RichLog, Static, OptionList
from textual.widgets.option_list import Option
from textual.binding import Binding
from rich.text import Text

from incalmo.cli.widgets import CommandSuggestionPopup, HostsWidget
from incalmo.cli.session import SessionManager
from incalmo.cli.commands_processor import CommandProcessor


class IncalmoREPL(App):
    """A Textual-based REPL for Incalmo CLI."""

    CSS_PATH = Path(__file__).parent / "repl.css"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True, priority=True),
        Binding("ctrl+l", "clear_output", "Clear", show=True),
        Binding("escape", "handle_escape", "Quit/Hide", show=False),
        Binding("down", "suggestion_down", "Next suggestion", show=False),
        Binding("up", "suggestion_up", "Previous suggestion", show=False),
        Binding("tab", "suggestion_select", "Select suggestion", show=False),
    ]

    def __init__(self):
        super().__init__(ansi_color=True)
        self.session_manager = SessionManager()
        self.command_processor = CommandProcessor(self.session_manager)
        self.suggestion_popup_visible = False

    def compose(self) -> ComposeResult:
        yield Header(icon="")

        with Container(classes="main-container"):
            with Container(classes="content-container"):
                with Container(classes="output-container"):
                    yield RichLog(id="output", markup=True)

                with Container(classes="sidebar-container"):
                    yield HostsWidget()

            with Container(classes="input-container"):
                yield Input(
                    placeholder="Type text or /command and press Enter...", id="input"
                )

        # Add the command suggestion popup as an overlay (initially hidden)
        yield CommandSuggestionPopup()

    def on_mount(self) -> None:
        self.title = "Incalmo"
        output = self.query_one("#output", RichLog)
        self.theme = "tokyo-night"

        # Welcome message with theme colors
        welcome_text = Text.assemble(
            ("Incalmo: The next generation of hacking\n\n"),
            ("/ to call expert agents\n"),
        )
        output.write(welcome_text)

        input_widget = self.query_one("#input", Input)
        input_widget.focus()

    def on_input_changed(self, message: Input.Changed) -> None:
        """Handle input changes to show/hide command suggestions."""
        value = str(message.value)

        if value == "/":
            # Show popup when user types just "/"
            self._show_suggestion_popup()
        elif value.startswith("/") and len(value) > 1:
            # Filter suggestions based on what user is typing
            self._filter_suggestions(value[1:])  # Remove the leading "/"
        else:
            # Hide popup if not typing a command
            self._hide_suggestion_popup()

    def on_option_list_option_selected(
        self, message: OptionList.OptionSelected
    ) -> None:
        """Handle selection from the suggestion popup."""
        if isinstance(message.option_list, CommandSuggestionPopup):
            # Set the input to the selected command
            input_widget = self.query_one("#input", Input)
            selected_text = str(message.option.prompt)
            input_widget.value = selected_text
            input_widget.cursor_position = len(selected_text)
            self._hide_suggestion_popup()
            input_widget.focus()

    def on_input_submitted(self, message: Input.Submitted) -> None:
        command = message.value.strip()
        if not command:
            return

        output = self.query_one("#output", RichLog)
        # Format command prompt with better styling
        prompt_text = Text.assemble(("❯ ", "bold cyan"), (command, "white"))
        output.write(prompt_text)

        # Clear input
        message.input.value = ""

        # Hide popup when command is submitted
        self._hide_suggestion_popup()

        # Process command
        result = self.command_processor.process_command(command, output)

        # Handle exit command
        if result == "exit":
            self.exit()

    def action_clear_output(self) -> None:
        """Clear the output log."""
        output = self.query_one("#output", RichLog)
        output.clear()

        cleared_text = Text.assemble(
            ("✨ ", "green"),
            ("Output cleared. Type ", "dim white"),
            ("help", "cyan"),
            (" for available commands.", "dim white"),
        )
        output.write(cleared_text)

    def action_handle_escape(self) -> None:
        """Handle escape key - hide popup if visible, otherwise quit."""
        if self.suggestion_popup_visible:
            self._hide_suggestion_popup()
        else:
            self.exit()

    def action_suggestion_down(self) -> None:
        """Move down in suggestion list."""
        if self.suggestion_popup_visible:
            popup = self.query_one(CommandSuggestionPopup)
            popup.action_cursor_down()

    def action_suggestion_up(self) -> None:
        """Move up in suggestion list."""
        if self.suggestion_popup_visible:
            popup = self.query_one(CommandSuggestionPopup)
            popup.action_cursor_up()

    def action_suggestion_select(self) -> None:
        """Select the highlighted suggestion."""
        if self.suggestion_popup_visible:
            popup = self.query_one(CommandSuggestionPopup)
            if popup.highlighted is not None:
                selected_option = popup.get_option_at_index(popup.highlighted)
                if selected_option:
                    # Set the input to the selected command
                    input_widget = self.query_one("#input", Input)
                    selected_text = str(selected_option.prompt)
                    input_widget.value = selected_text
                    input_widget.cursor_position = len(selected_text)
                    self._hide_suggestion_popup()

    def _show_suggestion_popup(self) -> None:
        """Show the command suggestion popup."""
        popup = self.query_one(CommandSuggestionPopup)

        # Show the popup
        popup.styles.display = "block"
        popup.styles.visibility = "visible"
        self.suggestion_popup_visible = True

    def _hide_suggestion_popup(self) -> None:
        """Hide the command suggestion popup."""
        popup = self.query_one(CommandSuggestionPopup)
        popup.styles.display = "none"
        popup.styles.visibility = "hidden"
        self.suggestion_popup_visible = False

    def _filter_suggestions(self, partial_command: str) -> None:
        """Filter suggestions based on partial command input."""
        popup = self.query_one(CommandSuggestionPopup)

        # Get available commands from command processor
        all_commands = self.command_processor.get_available_commands()

        # Filter commands that match the partial input
        matching_commands = [
            (cmd, desc)
            for cmd, desc in all_commands
            if cmd.startswith(partial_command.lower())
        ]

        if matching_commands:
            # Update popup with filtered options
            options = [Option(f"/{cmd}", id=cmd) for cmd, desc in matching_commands]
            popup.clear_options()
            popup.add_options(options)
            popup.styles.display = "block"
            popup.styles.visibility = "visible"
        else:
            # Hide if no matches
            self._hide_suggestion_popup()
