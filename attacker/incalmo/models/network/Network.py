from .Host import Host
from .Subnet import Subnet
from app.objects.c_agent import Agent
from .AttackPath import AttackPath, AttackTechnique
from plugins.deception.app.helpers.logging import log_event


class Network:
    def __init__(self, subnets: list[Subnet]):
        self.subnets = subnets
        # List of hosts that have unknown subnet
        self.unknown_hosts: list[Host] = []

    def get_all_hosts(self) -> list[Host]:
        all_hosts = []
        for subnet in self.subnets:
            all_hosts.extend(subnet.hosts)

        all_hosts.extend(self.unknown_hosts)

        return all_hosts

    def find_host_by_hostname(self, hostname: str):
        for subnet in self.subnets:
            for host in subnet.hosts:
                if host.hostname == hostname:
                    return host

        for host in self.unknown_hosts:
            if host.hostname == hostname:
                return host

        return None

    def find_host_by_ip(self, host_ip: str):
        for subnet in self.subnets:
            for host in subnet.hosts:
                if host.ip_address == host_ip:
                    return host

        for host in self.unknown_hosts:
            if host.ip_address == host_ip:
                return host

        return None

    def find_agent_for_host(self, host: Host, username: str | None = None):
        for agent in host.agents:
            if host.ip_address in agent.host_ip_addrs:
                if username is not None and agent.username == username:
                    return agent
                elif username is None:
                    return agent

        return None

    def find_host_by_agent(self, agent: Agent):
        for subnet in self.subnets:
            for host in subnet.hosts:
                if host.ip_address in agent.host_ip_addrs:
                    return host

        for host in self.unknown_hosts:
            if host.ip_address in agent.host_ip_addrs:
                return host

        return None

    def get_uninfected_hosts(self):
        uninfected_hosts = []
        for subnet in self.subnets:
            for host in subnet.hosts:
                if not host.infected:
                    uninfected_hosts.append(host)

        for host in self.unknown_hosts:
            if not host.infected:
                uninfected_hosts.append(host)

        return uninfected_hosts

    def find_subnet_by_host(self, host: Host | None):
        if host is None:
            return None

        for subnet in self.subnets:
            for subnet_host in subnet.hosts:
                if subnet_host == host:
                    return subnet

        return None

    def find_subnet_by_ip_mask(self, ip_mask: str):
        for subnet in self.subnets:
            if subnet.ip_mask == ip_mask:
                return subnet

        return None

    def add_host(self, host: Host):
        if host.ip_address is None:
            return

        for subnet in self.subnets:
            if subnet.is_ip_in_ipmask(host.ip_address):
                subnet.add_host(host)
                return

        self.unknown_hosts.append(host)

    def add_subnet(self, subnet: Subnet):
        self.subnets.append(subnet)

    def get_all_subnets(self, include_attacker_subnets: bool = False):
        subnets = []
        for subnet in self.subnets:
            if subnet.attacker_subnet:
                if include_attacker_subnets:
                    subnets.append(subnet)
                else:
                    continue
            else:
                subnets.append(subnet)
        return subnets

    def get_non_infected_subnets(self):
        subnets = []
        for subnet in self.subnets:
            infected = False
            for host in subnet.hosts:
                if host.is_infected():
                    infected = True
                    break
            if not infected:
                subnets.append(subnet)

        return subnets

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.subnets}"
