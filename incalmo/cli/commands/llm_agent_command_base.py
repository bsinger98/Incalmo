#!/usr/bin/env python3
"""
Base class for CLI commands that spawn specific LLM agents
"""
from abc import ABC, abstractmethod
from rich.text import Text
from textual.widgets import RichLog
import asyncio
from uuid import uuid4

from incalmo.cli.commands.base import BaseCommand
from incalmo.core.actions.HighLevel.llm_agents.llm_agent_action import LLMAgentAction
from incalmo.core.services.action_context import HighLevelContext


class LLMAgentCommand(BaseCommand, ABC):
    """Base class for commands that spawn specific LLM agents."""
    
    @abstractmethod
    def get_agent_action(self, args: str) -> str:
        """Get the LLM agent action name (e.g., 'scan', 'lateral_move')."""
        pass
    
    @abstractmethod
    def get_agent_params(self, args: str) -> dict:
        """Get the parameters dictionary for the LLM agent."""
        pass

    def _initialize_llm(self, output: RichLog) -> bool:
        """Initialize the LLM interface and store it in the session. Returns True if successful."""
        try:
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
    
    def execute(self, args: str, output: RichLog) -> str | None:
        """Execute the LLM agent action."""

        if not self._ensure_llm_initialized(output):
            error_text = Text.assemble(
                ("❌ ", "red"),
                ("Failed to initialize LLM agent. Command aborted.", "red"),
            )
            output.write(error_text)
            return None
        
        llm_strategy = self.session.get_strategy()
        
        if not llm_strategy:
            error_text = Text.assemble(
                ("❌ ", "red"),
                ("LLM strategy not configured. Please set it up first.", "red"),
            )
            output.write(error_text)
            return None
            
        try:
            # Get the agent action and params
            action_name = self.get_agent_action(args)
            params = self.get_agent_params(args)
            
            output.write(
                Text.assemble(
                    ("⏳ ", "yellow"), 
                    (f"Initializing {action_name} agent with params: {params}", "yellow")
                )
            )
            
            # Get the LLM agent action from registry
            from incalmo.models.llm_agent_action_data import LLMAgentActionData
            action_data = LLMAgentActionData(action=action_name, params=params)
            
            agent_action = llm_strategy.agent_registry.get_llm_agent_action(action_data).from_params(
                params, llm_strategy.agent_interface
            )
            
            # Execute the agent action
            output.write(
                Text.assemble(
                    ("🚀 ", "green"), 
                    (f"Executing {action_name} agent...", "green")
                )
            )
            
            result = self._execute_agent_action(agent_action, llm_strategy)
            
            if result:
                output.write(
                    Text.assemble(
                        ("✅ ", "green"), 
                        (f"Agent {action_name} completed successfully", "green")
                    )
                )
                # Display any events or results
                for event in result:
                    output.write(Text(f"Event: {event}", style="dim white"))
            else:
                output.write(
                    Text.assemble(
                        ("⚠️ ", "yellow"), 
                        (f"Agent {action_name} completed with no results", "yellow")
                    )
                )
                
        except Exception as e:
            output.write(
                Text.assemble(
                    ("❌ ", "red"),
                    (f"Error executing agent: {str(e)}", "red"),
                )
            )
            
        return None
    
    def _execute_agent_action(self, agent_action: LLMAgentAction, llm_strategy):
        """Execute the agent action asynchronously."""
        def run_agent():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                hl_id = str(uuid4())
                context = HighLevelContext(hl_id=hl_id)
                
                # Run the agent action
                routine = agent_action.run(
                    llm_strategy.low_level_action_orchestrator,
                    llm_strategy.environment_state_service,
                    llm_strategy.attack_graph_service,
                    context
                )
                result = new_loop.run_until_complete(routine)
                return result
            finally:
                new_loop.close()

        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_agent)
            result = future.result()  # Wait for completion
            return result