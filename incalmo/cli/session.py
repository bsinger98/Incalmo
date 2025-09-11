#!/usr/bin/env python3
"""
Session management for Incalmo CLI REPL
"""

from typing import Dict, Any


class SessionManager:
    """Manages session data and state for the REPL."""

    def __init__(self):
        self.data: Dict[str, Any] = {}

    def set_variable(self, key: str, value: str) -> None:
        """Set a session variable."""
        self.data[key] = value

    def get_variable(self, key: str) -> str | None:
        """Get a session variable."""
        return self.data.get(key)

    def has_variable(self, key: str) -> bool:
        """Check if a variable exists."""
        return key in self.data

    def clear_variables(self) -> None:
        """Clear all session variables."""
        self.data.clear()

    def get_variable_count(self) -> int:
        """Get the count of session variables."""
        return len(self.data)

    def get_variable_keys(self) -> list[str]:
        """Get all variable keys."""
        return list(self.data.keys())

    def get_status_text(self) -> str:
        """Get status bar text."""
        return f"📊 Variables: {len(self.data)} | ⚡ Commands: 10 | 🚀 Incalmo CLI REPL"
