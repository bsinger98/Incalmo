from abc import ABC, abstractmethod
from rich.text import Text
from textual.widgets import RichLog
from typing import TYPE_CHECKING
import asyncio

from incalmo.cli.commands.base import BaseCommand
from incalmo.core.actions.high_level_action import HighLevelAction
from incalmo.core.actions.HighLevel.llm_agents.llm_agent_action import (
    LLMAgentAction,
)

class BaseLLMCommand(BaseCommand):  # Extend BaseCommand
    """Base class for commands that use LLM strategy execution."""
    
    def _initialize_llm(self, output: RichLog) -> bool:
        """Initialize the LLM interface and store it in the session. Returns True if successful."""
        try:
            output.write(
                Text.assemble(
                    ("🚀 ", "green"), ("Initializing LLM agent for your request...", "yellow")
                )
            )
            from incalmo.core.services.config_service import ConfigService
            from incalmo.core.strategies.strategy_factory import StrategyFactory

            config = ConfigService().get_config()
            
            cli_task_id = f"cli_session_{config.name}"
            strategy = StrategyFactory().build_strategy(config, task_id=cli_task_id)

            # Run initialization in a separate thread to avoid event loop conflict
            def init_strategy_sync():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    new_loop.run_until_complete(strategy.initialize())
                finally:
                    new_loop.close()

            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(init_strategy_sync)
                future.result()  # Wait for completion

            self.session.set_strategy(strategy)
            
            return True
        except Exception as e:
            output.write(
                Text.assemble(
                    ("❌ ", "red"), (f"Error initializing LLM agent: {e}", "red")
                )
            )
            return False

    def _ensure_llm_initialized(self, output: RichLog) -> bool:
        """Ensure LLM is initialized, initialize if needed. Returns True if available."""
        if self.session.get_strategy() is None:
            return self._initialize_llm(output)
        return True
        
    # Implements the abstract execute() method from BaseCommand
    def execute(self, args: str, output: RichLog) -> str | None:
        """Common LLM execution logic here"""

        if not self._ensure_llm_initialized(output):
            error_text = Text.assemble(
                ("❌ ", "red"),
                ("Failed to initialize LLM agent. Command aborted.", "red"),
            )
            output.write(error_text)
            return None
        
        request_text = Text.assemble(
            ("🔍 ", "cyan"),
            ("Request: ", "cyan"),
            (args if args else "No additional details provided", "white"),
        )
        output.write(request_text)

        llm_strategy = self.session.get_strategy()

        if not llm_strategy or not llm_strategy.llm_interface:
            error_text = Text.assemble(
                ("❌ ", "red"),
                ("LLM interface not configured. Please set it up first.", "red"),
            )
            output.write(error_text)
            return None

        try:
            output.write(
                Text.assemble(
                    ("⏳ ", "yellow"), ("Processing request...", "yellow")
                )
            )

            llm_strategy.last_response = args
            agents = llm_strategy.c2_client.get_agents()
            llm_strategy.environment_state_service.update_host_agents(agents)

            
            while True:
                finished, result = self._execute_llm_request(llm_strategy)

                if "Error executing query or action:" in result: 
                    # Display error and continue
                    output.write(
                        Text.assemble(
                            ("⚠️ ", "yellow"), (f"Step {step_count} had an issue, retrying...", "yellow")
                        )
                    )
                    continue
                else:
                    output.write(Text(str(llm_strategy.last_response), style="white"))
                    return None

        except Exception as e:
            output.write(
                Text.assemble(
                    ("❌ ", "red"),
                    (f"Error during request: {str(e)}", "red"),
                )
            )

        return None

    def _execute_llm_request(self, llm_strategy):
        def run_llm_request():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                routine = llm_strategy.llm_request()
                result = new_loop.run_until_complete(routine)
                return result, llm_strategy.last_response
            finally:
                new_loop.close()

        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_llm_request)
            finished, result = future.result()  # Wait for completion
            return finished, result
