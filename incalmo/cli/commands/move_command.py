#!/usr/bin/env python3
"""
Lateral movement command for Incalmo CLI
"""
from incalmo.cli.commands.llm_agent_command_base import LLMAgentCommand


class MoveCommand(LLMAgentCommand):
    """Perform lateral movement operations using LLM agent."""

    @property
    def name(self) -> str:
        return "move"

    @property
    def description(self) -> str:
        return "Perform lateral movement operations"

    @property
    def aliases(self) -> list[str]:
        """Alternative names for this command."""
        return ["lateral", "pivot"]

    def get_agent_action(self, args: str) -> str:
        """Get the LLM agent action name."""
        return "lateral_move"
    
    def get_agent_params(self, args: str) -> dict:
        """Get the parameters for the lateral movement agent."""
        parts = args.strip().split()
        
        if len(parts) >= 2:
            # User provided source and target hosts
            src_host = parts[0]
            target_host = parts[1]
        else:
            # Try to infer from environment state
            llm_strategy = self.session.get_strategy()
            if llm_strategy and llm_strategy.environment_state_service.initial_hosts:
                initial_host = llm_strategy.environment_state_service.initial_hosts[0]
                src_host = initial_host.ip_addresses[0] if initial_host.ip_addresses else "127.0.0.1"
                
                if len(parts) == 1:
                    target_host = parts[0]
                else:
                    target_host = "192.168.1.100"  # Default target
            else:
                src_host = "127.0.0.1"
                target_host = "192.168.1.100"
        
        return {
            "src_host": src_host,
            "target_host": target_host
        }