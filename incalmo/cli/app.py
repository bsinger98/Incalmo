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
from incalmo.incalmo_runner import run_incalmo_strategy


class IncalmoREPL(App):
    """A Textual-based REPL for Incalmo CLI."""

    CSS_PATH = Path(__file__).parent / "repl.css"

    BINDINGS = [
        Binding("ctrl+c", "cancel_or_quit", "Cancel/Quit", show=True, priority=True),
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
        self.running_workers = {}  # Track running workers by ID for cancellation
        self.worker_counter = 0  # Simple counter for unique worker IDs

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

        if self._should_run_async(command):
            
            queued_text = Text.assemble(
                ("📝 ", "blue"), ("Command queued for processing...", "blue")
            )
            output.write(queued_text)

            # Process LLM commands asynchronously
            self.worker_counter += 1
            worker_id = self.worker_counter
            worker = self.run_worker(self._execute_command_async(command, output, worker_id), exclusive=False)
            self.running_workers[worker_id] = worker
        else:
            result = self.command_processor.process_command(command, output)
            if result == "exit":
                self.exit()

    def _should_run_async(self, command: str) -> bool:
        """Check if a command should be run asynchronously."""

        if not command.startswith("/"):
            return True
            
        parts = command[1:].split(None, 1)
        if not parts:
            return False
            
        cmd_name = parts[0].lower()
        command_obj = self.command_processor.registry.get_command(cmd_name)
        
        if command_obj:
            from incalmo.cli.commands.llm_command_base import BaseLLMCommand
            from incalmo.cli.commands.llm_agent_command_base import LLMAgentCommand
            return isinstance(command_obj, (BaseLLMCommand, LLMAgentCommand)) #LLM based commands should be async
        
        # Unknown commands default to sync
        return False

    async def _execute_command_async(self, command: str, output: RichLog, worker_id: int) -> None:
        """Execute command asynchronously to keep UI responsive."""
        try:
            # Process command
            result = await self._run_command_in_thread(command, output)

        except asyncio.CancelledError:
            # Handle cancellation gracefully
            cancel_text = Text.assemble(
                ("🛑 ", "red"), ("Command cancelled by user.", "red")
            )
            output.write(cancel_text)
            raise  # Re-raise to properly handle cancellation
        except Exception as e:
            error_text = Text.assemble(
                ("❌ ", "red"), (f"Error executing command: {e}", "red")
            )
            output.write(error_text)
        finally:
            self.running_workers.pop(worker_id, None)

    async def _run_command_in_thread(self, command: str, output: RichLog) -> str | None:
        """Run command in a thread pool to avoid blocking the UI."""
        import asyncio
        import concurrent.futures
        
        def run_command():
            return self.command_processor.process_command(command, output)
            
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, run_command)

    def action_cancel_or_quit(self) -> None:
        """Cancel running commands or quit if none are running."""
        if self.running_workers:
            # Cancel all running workers
            output = self.query_one("#output", RichLog)
            for worker in list(self.running_workers.values()):
                worker.cancel()
            
            self.running_workers.clear()
            
            cancel_text = Text.assemble(
                ("🛑 ", "red"), ("Cancelled running commands.", "red")
            )
            output.write(cancel_text)
        else:
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
