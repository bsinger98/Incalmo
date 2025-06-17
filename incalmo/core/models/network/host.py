from .credential import SSHCredential
from incalmo.core.models.attacker.agent import Agent
import random

from incalmo.core.models.network.open_port import OpenPort


class Host:
    def __init__(
        self,
        ip_addresses: list[str] | None = None,
        hostname: str | None = None,
        users: dict[str, str] | None = None,
        open_ports: dict[int, OpenPort] | None = None,
        agents: list[Agent] | None = None,
        infection_source_agent: Agent | None = None,
    ):
        self.hostname = hostname
        self.ip_addresses = ip_addresses if ip_addresses is not None else []
        self.users = users if users is not None else {}
        self.open_ports: dict[int, OpenPort] = (
            open_ports if open_ports is not None else {}
        )

        # SSH config is a list of tuples of (username, hostname)
        self.ssh_config: list[SSHCredential] = []

        # Dict mapping user to list of critical data files
        self.critical_data_files: dict[str, list[str]] = {}
        self.agents: list[Agent] = agents if agents is not None else []

        self.infected = len(self.agents) > 0
        self.infection_source_agent = infection_source_agent or None

    def __str__(self):
        agent_names = [agent.paw for agent in self.agents]
        return (
            f"{self.__class__.__name__}: "
            f"hostname: {self.hostname} - "
            f"ip: {self.ip_addresses} - "
            f"users: {self.users} - "
            f"open_ports: {self.open_ports} - "
            f"agents: {agent_names} - "
            f"ssh_config: {self.ssh_config} - "
            f"critical_data_files: {self.critical_data_files} - "
            f"infected_by: {self.infection_source_agent.paw if self.infection_source_agent else None}"
        )

    def to_dict(self) -> dict:
        return {
            "hostname": self.hostname,
            "ip_addresses": self.ip_addresses,
            "infected": self.infected,
            "agents": [agent.paw for agent in self.agents],
            "infected_by": self.infection_source_agent.paw
            if self.infection_source_agent
            else None,
        }

    def get_port_for_service(self, service: str):
        for port, cur_service in self.open_ports.items():
            if cur_service.service == service:
                return port

        return None

    def has_service(self, service: str):
        if self.get_port_for_service(service) is not None:
            return True

        return False

    def has_agent(self, agent: Agent):
        for host_agent in self.agents:
            if host_agent.paw == agent.paw:
                return True
        return False

    def add_agent(self, agent: Agent):
        self.infected = True
        self.agents.append(agent)

    def get_agent(self):
        if len(self.agents) > 0:
            return random.choice(self.agents)
        return None

    def get_agent_by_username(self, username: str):
        for agent in self.agents:
            if agent.username == username:
                return agent
        return None

    def is_infected(self):
        return self.infected

    def get_ip_address(self):
        return random.choice(self.ip_addresses)

    def has_an_ip_address(self):
        return len(self.ip_addresses) > 0

    @classmethod
    def merge(cls, host1: "Host", host2: "Host") -> "Host":
        """
        Create a new Host by merging two existing hosts.

        Args:
            host1: First host to merge
            host2: Second host to merge

        Returns:
            New Host instance with merged data from both input hosts
        """
        # Handle hostname - prefer the first one if both exist, otherwise use whichever exists
        merged_hostname = host1.hostname if host1.hostname else host2.hostname

        # Merge IP addresses and remove duplicates
        merged_ip_addresses = list(set(host1.ip_addresses + host2.ip_addresses))

        # Merge users dictionaries (host2 values will override host1 if same key)
        merged_users = {**host1.users, **host2.users}

        # Merge open_ports dictionaries (host2 values will override host1 if same port)
        merged_open_ports = {**host1.open_ports, **host2.open_ports}

        # Merge agents lists
        merged_agents = host1.agents + host2.agents

        # Merge infection source
        merged_infection_source_agent = (
            host1.infection_source_agent
            if host1.infection_source_agent
            else host2.infection_source_agent
        )

        # Create new host with merged data
        merged_host = cls(
            ip_addresses=merged_ip_addresses,
            hostname=merged_hostname,
            users=merged_users,
            open_ports=merged_open_ports,
            agents=merged_agents,
            infection_source_agent=merged_infection_source_agent,
        )

        # Merge ssh_config lists
        merged_host.ssh_config = host1.ssh_config + host2.ssh_config

        # Merge critical_data_files dictionaries
        merged_critical_data_files = {}
        for user, files in host1.critical_data_files.items():
            merged_critical_data_files[user] = files.copy()

        for user, files in host2.critical_data_files.items():
            if user in merged_critical_data_files:
                # Combine file lists and remove duplicates
                merged_critical_data_files[user] = list(
                    set(merged_critical_data_files[user] + files)
                )
            else:
                merged_critical_data_files[user] = files.copy()

        merged_host.critical_data_files = merged_critical_data_files

        return merged_host
