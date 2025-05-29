from .Credential import SSHCredential
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
    ):
        self.ip_addresses = ip_addresses
        self.hostname = hostname
        self.users = users

        self.users = users if users is not None else {}
        self.open_ports: dict[int, OpenPort] = (
            open_ports if open_ports is not None else {}
        )

        # SSH config is a list of tuples of (username, hostname)
        self.ssh_config: list[SSHCredential] = []

        # Dict mapping user to list of critical data files
        self.critical_data_files: dict[str, list[str]] = {}
        self.agents: list[Agent] = agents if agents is not None else []

        if len(self.agents) > 0:
            self.infected = True
        else:
            self.infected = False

    def __str__(self):
        agent_names = [agent.paw for agent in self.agents]
        return f"{self.__class__.__name__}: hostname: {self.hostname} - ip: {self.ip_addresses} - users: {self.users} - open_ports: {self.open_ports} - agents: {agent_names} - ssh_config: {self.ssh_config} - critical_data_files: {self.critical_data_files}"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Host):
            return False
        return (
            self.ip_addresses == __value.ip_addresses
            or self.hostname == __value.hostname
        )

    def get_port_for_service(self, service: str):
        for port, cur_service in self.open_ports.items():
            if cur_service.service == service:
                return port

        return None

    def has_service(self, service: str):
        if self.get_port_for_service(service) is not None:
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
        if len(self.agents) > 0:
            return True
