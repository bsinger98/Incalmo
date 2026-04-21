#!/usr/bin/env python3
"""
General LLM command for Incalmo CLI
"""
from incalmo.cli.commands.llm_command_base import BaseLLMCommand


class LLMCommand(BaseLLMCommand):
    """Perform general LLM based operations."""

    @property
    def name(self) -> str:
        return "llm"

    @property
    def description(self) -> str:
        return "Perform general LLM-based commands with an Incalmo agent"

    @property
    def aliases(self) -> list[str]:
        """Alternative names for this command."""
        return []

    