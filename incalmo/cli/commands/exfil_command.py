#!/usr/bin/env python3
"""
Data exfiltration command for Incalmo CLI using LLM agent
"""
from incalmo.cli.commands.llm_agent_command_base import LLMAgentCommand


class ExfilCommand(LLMAgentCommand):
    """Perform data exfiltration operations using LLM agent."""

    @property
    def name(self) -> str:
        return "exfil"

    @property
    def description(self) -> str:
        return "Exfiltrate data from compromised hosts"

    @property
    def aliases(self) -> list[str]:
        """Alternative names for this command."""
        return ["extract", "steal"]

    def get_agent_action(self, args: str) -> str:
        """Get the LLM agent action name."""
        return "exfiltrate"
    
    def get_agent_params(self, args: str) -> dict:
        """Get the parameters for the data exfiltration agent."""
        if args.strip():
            # If user provided a host IP, use it
            host = args.strip().split()[0]
        else:
            # Default to exfiltrating from the first available agent host
            llm_strategy = self.session.get_strategy()
            if llm_strategy and llm_strategy.environment_state_service.initial_hosts:
                initial_host = llm_strategy.environment_state_service.initial_hosts[0]
                host = initial_host.ip_addresses[0] if initial_host.ip_addresses else "127.0.0.1"
            else:
                host = "127.0.0.1"
        
        return {
            "host": host
        }