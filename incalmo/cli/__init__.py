#!/usr/bin/env python3
"""
Incalmo CLI Package

A modular CLI interface for Incalmo with REPL functionality.
"""

from incalmo.cli.app import IncalmoREPL
from incalmo.cli.session import SessionManager
from incalmo.cli.commands_processor import CommandProcessor
from incalmo.cli.widgets import CommandSuggestionPopup

__all__ = [
    "IncalmoREPL",
    "SessionManager",
    "CommandProcessor",
    "CommandSuggestionPopup",
]
