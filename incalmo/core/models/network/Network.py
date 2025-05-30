from .Host import Host
from .Subnet import Subnet
from incalmo.core.models.attacker.agent import Agent


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
                if len(host.ip_addresses) > 0 and host_ip in host.ip_addresses:
                    return host

        for host in self.unknown_hosts:
            if len(host.ip_addresses) > 0 and host_ip in host.ip_addresses:
                return host

        return None

    def find_agent_for_host(self, host: Host, username: str | None = None):
        for agent in host.agents:
            if len(host.ip_addresses) > 0 and any(
                ip in agent.host_ip_addrs for ip in host.ip_addresses
            ):
                if username is not None and agent.username == username:
                    return agent
                elif username is None:
                    return agent

        return None

    def find_host_by_agent(self, agent: Agent):
        for subnet in self.subnets:
            for host in subnet.hosts:
                if len(host.ip_addresses) > 0 and any(
                    ip in agent.host_ip_addrs for ip in host.ip_addresses
                ):
                    return host

        for host in self.unknown_hosts:
            if len(host.ip_addresses) > 0 and any(
                ip in agent.host_ip_addrs for ip in host.ip_addresses
            ):
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

    def find_common_subnet(self, host1: Host, host2: Host):
        for subnet in self.subnets:
            if any(subnet.is_ip_in_ipmask(ip) for ip in host1.ip_addresses) and any(
                subnet.is_ip_in_ipmask(ip) for ip in host2.ip_addresses
            ):
                return subnet
        return None

    def find_ip_in_common_subnet(self, attacking_host: Host, host_to_attack: Host):
        common_subnet = self.find_common_subnet(attacking_host, host_to_attack)
        if common_subnet:
            return common_subnet.find_ip_in_subnet(host_to_attack.ip_addresses)
        return None

    def add_host(self, host: Host):
        if len(host.ip_addresses) == 0:
            return

        # Check if any of the host's IPs already exist in the network
        for ip in host.ip_addresses:
            existing_host = self.find_host_by_ip(ip)
            if existing_host:  # If host with IP already exists, combine information
                existing_host.merge_from_host(host)
                host = existing_host
        is_in_subnet = False
        for subnet in self.subnets:
            for ip_address in host.ip_addresses:
                if subnet.is_ip_in_ipmask(ip_address):
                    if host not in subnet.hosts:
                        subnet.add_host(host)
                    is_in_subnet = True
        if not is_in_subnet:
            # If host does not match any existing subnet, add it to unknown_hosts
            self.unknown_hosts.append(host)

        return host

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
