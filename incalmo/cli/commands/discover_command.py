#!/usr/bin/env python3
"""
Discover command for Incalmo CLI
"""
from incalmo.cli.commands.llm_agent_command_base import LLMAgentCommand


class DiscoverCommand(LLMAgentCommand):
    """Perform network discovery operations using LLM scan agent."""

    @property
    def name(self) -> str:
        return "discover"

    @property
    def description(self) -> str:
        return "Perform network discovery and scanning operations"

    @property
    def aliases(self) -> list[str]:
        """Alternative names for this command."""
        return ["scan", "recon"]

    def get_agent_action(self, args: str) -> str:
        """Get the LLM agent action name."""
        return "scan"
    
    def get_agent_params(self, args: str) -> dict:
        """Get the parameters for the scan agent."""
        if args.strip():
            scan_host = args.strip().split()[0]
        else:
            # Default to scanning from the first available agent
            llm_strategy = self.session.get_strategy()
            if llm_strategy and llm_strategy.environment_state_service.initial_hosts:
                initial_host = llm_strategy.environment_state_service.initial_hosts[0]
                if initial_host.ip_addresses:
                    scan_host = initial_host.ip_addresses[0]
                else:
                    # Fallback to localhost if no IP addresses available
                    scan_host = "127.0.0.1"
            else:
                scan_host = "127.0.0.1"
        
        return {
            "scan_host": scan_host
        }