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
                if host.ip_addresses and host_ip in host.ip_addresses:
                    return host

        for host in self.unknown_hosts:
            if host.ip_addresses and host_ip in host.ip_addresses:
                return host

        return None

    def find_agent_for_host(self, host: Host, username: str | None = None):
        for agent in host.agents:
            if host.ip_addresses and any(
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
                if host.ip_addresses and any(
                    ip in agent.host_ip_addrs for ip in host.ip_addresses
                ):
                    return host

        for host in self.unknown_hosts:
            if host.ip_addresses and any(
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

    def add_host(self, host: Host):
        if host.ip_addresses is None:
            return

        # Check if any of the host's IPs already exist in the network
        for ip in host.ip_addresses:
            existing_host = self.find_host_by_ip(ip)
            if existing_host:
                # Merge IPs
                for new_ip in host.ip_addresses:
                    if (
                        existing_host.ip_addresses
                        and new_ip not in existing_host.ip_addresses
                    ):
                        existing_host.ip_addresses.append(new_ip)
                return existing_host
        for subnet in self.subnets:
            for ip_address in host.ip_addresses:
                if subnet.is_ip_in_ipmask(ip_address):
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

    def deduplicate_hosts(self):
        ip_to_host = {}
        all_hosts = []

        # Collect all hosts from all subnets and unknown_hosts
        for subnet in self.subnets:
            all_hosts.extend(subnet.hosts)
        all_hosts.extend(self.unknown_hosts)

        # Merge hosts by IP
        for host in all_hosts:
            for ip in host.ip_addresses:
                if ip in ip_to_host:
                    existing = ip_to_host[ip]
                    # Merge IPs
                    for new_ip in host.ip_addresses:
                        if new_ip not in existing.ip_addresses:
                            existing.ip_addresses.append(new_ip)
                    # Merge agents
                    for agent in getattr(host, "agents", []):
                        if agent not in existing.agents:
                            existing.agents.append(agent)
                    # Merge open_ports
                    for port, port_obj in getattr(host, "open_ports", {}).items():
                        if port not in existing.open_ports:
                            existing.open_ports[port] = port_obj
                    # Merge ssh_config
                    if hasattr(host, "ssh_config"):
                        for cred in host.ssh_config:
                            if cred not in existing.ssh_config:
                                existing.ssh_config.append(cred)
                    # After merging, update all mappings for all IPs to point to the merged host
                    for merged_ip in existing.ip_addresses:
                        ip_to_host[merged_ip] = existing
                    # Sort IPs for consistency
                    existing.ip_addresses.sort()
                else:
                    ip_to_host[ip] = host

        # Now, for each subnet, replace hosts with deduplicated ones
        for subnet in self.subnets:
            unique_hosts = []
            seen = set()
            for host in subnet.hosts:
                # Use any IP to get the deduped host (all IPs now map to the same object)
                dedup_host = ip_to_host[host.ip_addresses[0]]
                if id(dedup_host) not in seen:
                    unique_hosts.append(dedup_host)
                    seen.add(id(dedup_host))
            subnet.hosts = unique_hosts

        # Same for unknown_hosts
        unique_hosts = []
        seen = set()
        for host in self.unknown_hosts:
            dedup_host = ip_to_host[host.ip_addresses[0]]
            if id(dedup_host) not in seen:
                unique_hosts.append(dedup_host)
                seen.add(id(dedup_host))
        self.unknown_hosts = unique_hosts

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.subnets}"
