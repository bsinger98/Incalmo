#!/usr/bin/env python3
"""
Privilege escalation command for Incalmo CLI using LLM agent
"""
from incalmo.cli.commands.llm_agent_command_base import LLMAgentCommand


class PrivEscCommand(LLMAgentCommand):
    """Perform privilege escalation operations using LLM agent."""

    @property
    def name(self) -> str:
        return "privesc"

    @property
    def description(self) -> str:
        return "Perform privilege escalation operations"

    @property
    def aliases(self) -> list[str]:
        """Alternative names for this command."""
        return ["escalate", "priv"]

    def get_agent_action(self, args: str) -> str:
        """Get the LLM agent action name."""
        return "privilege_escalation"
    
    def get_agent_params(self, args: str) -> dict:
        """Get the parameters for the privilege escalation agent."""
        if args.strip():
            # If user provided a host IP, use it
            host = args.strip().split()[0]
        else:
            # Default to escalating on the first available agent host
            llm_strategy = self.session.get_strategy()
            if llm_strategy and llm_strategy.environment_state_service.initial_hosts:
                initial_host = llm_strategy.environment_state_service.initial_hosts[0]
                host = initial_host.ip_addresses[0] if initial_host.ip_addresses else "127.0.0.1"
            else:
                host = "127.0.0.1"
        
        return {
            "host": host
        }