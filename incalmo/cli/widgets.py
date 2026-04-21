#!/usr/bin/env python3
"""
UI Widgets for Incalmo CLI REPL
"""

from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option
from rich.text import Text
from rich.table import Table
import requests
from typing import Dict, List, Any


class CommandSuggestionPopup(OptionList):
    """A popup widget that shows command suggestions."""

    def __init__(self) -> None:
        # Define available commands with descriptions
        commands = [
            ("help", "Show detailed help"),
            ("discover", "Perform discovery operations"),
            ("move", "Lateral movement operations"),
            ("privesc", "Privilege escalation operations"),
            ("exfil", "Data exfiltration operations"),
            ("exit", "Exit..."),
        ]

        options = [Option(f"/{cmd}", id=cmd) for cmd, desc in commands]

        super().__init__(*options)
        self.can_focus = False


class HostsWidget(Static):
    """A widget that displays a list of available hosts."""

    def __init__(self) -> None:
        super().__init__()
        self.hosts_data: List[Dict[str, Any]] = []
        self.api_server_url = "http://localhost:8888"  # Default API server URL

    def compose(self):
        """Compose the widget layout."""
        yield Static("Infected Hosts", classes="hosts-header")
        yield Static("Loading hosts...", id="hosts-content", classes="hosts-content")

    def on_mount(self) -> None:
        """Initialize the widget when mounted."""
        self.set_interval(5.0, self.refresh_hosts)  # Refresh every 5 seconds
        self.refresh_hosts()

    def refresh_hosts(self) -> None:
        """Fetch and display the latest host information."""
        try:
            # Try to get hosts from the API
            response = requests.get(f"{self.api_server_url}/hosts", timeout=2)
            if response.status_code == 200:
                data = response.json()
                hosts = data.get("hosts", [])
                self.update_hosts_display(hosts)
            else:
                self.show_error(f"API Error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            # If API is not available, show sample/mock data
            self.show_mock_data()
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def update_hosts_display(self, hosts: List[Dict[str, Any]]) -> None:
        """Update the display with host information."""
        if not hosts:
            content = Text("No hosts available", style="dim")
        else:
            # Create a rich table for better formatting
            table = Table(
                show_header=False, show_edge=False, pad_edge=False, expand=False
            )
            table.add_column("Info", style="white", width=30)

            for host in hosts[:8]:  # Limit to 8 hosts to avoid clutter
                hostname = host.get("hostname", "Unknown")
                ip_addresses = host.get("ip_addresses", [])
                infected = host.get("infected", False)
                agents = host.get("agents", [])

                # Format IP addresses
                ip_str = ", ".join(ip_addresses[:2]) if ip_addresses else "No IP"
                if len(ip_addresses) > 2:
                    ip_str += f" (+{len(ip_addresses) - 2} more)"

                # Create status indicator
                status_icon = "🔴" if infected else "⚪"
                agent_count = len(agents) if agents else 0

                # Format the host entry
                host_line = f"{status_icon} {hostname}"
                detail_line = f"   {ip_str}"
                if agent_count > 0:
                    detail_line += (
                        f" • {agent_count} agent{'s' if agent_count != 1 else ''}"
                    )

                table.add_row(host_line)
                table.add_row(Text(detail_line, style="dim"))

            content = table

        # Update the content
        content_widget = self.query_one("#hosts-content", Static)
        content_widget.update(content)

    def show_mock_data(self) -> None:
        """Show sample data when API is not available."""
        mock_hosts = [
            {
                "hostname": "web-server-01",
                "ip_addresses": ["192.168.1.10"],
                "infected": True,
                "agents": ["agent-001"],
            },
            {
                "hostname": "db-server-01",
                "ip_addresses": ["192.168.1.20"],
                "infected": False,
                "agents": [],
            },
            {
                "hostname": "app-server-01",
                "ip_addresses": ["192.168.1.30", "10.0.1.30"],
                "infected": True,
                "agents": ["agent-002", "agent-003"],
            },
        ]
        self.update_hosts_display(mock_hosts)

    def show_error(self, error_msg: str) -> None:
        """Show an error message."""
        content_widget = self.query_one("#hosts-content", Static)
        content_widget.update(Text(f"❌ {error_msg}", style="red"))
