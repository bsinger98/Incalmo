from .Host import Host

import ipaddress


class Subnet:
    def __init__(self, ip_mask: str, hosts=None, attacker_subnet: bool = False):
        self.ip_mask = ip_mask
        self.hosts: list[Host] = hosts if hosts is not None else []
        self.attacker_subnet = attacker_subnet

    def find_host_by_ip(self, host_ip: str) -> Host | None:
        for host in self.hosts:
            if host.ip_address == host_ip:
                return host

        return None

    def is_ip_in_ipmask(self, ip_address: str):
        return ipaddress.ip_address(ip_address) in ipaddress.ip_network(self.ip_mask)

    def add_host(self, host: Host):
        self.hosts.append(host)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.ip_mask}"
