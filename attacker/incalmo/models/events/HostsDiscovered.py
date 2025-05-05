from plugins.deception.app.models.events import Event


class HostsDiscovered(Event):
    def __init__(self, subnet_ip_mask: str, host_ips: list[str]):
        self.subnet_ip_mask = subnet_ip_mask
        self.host_ips = host_ips

    def __str__(self):
        return f"HostsDiscovered: {self.subnet_ip_mask} - {self.host_ips}"
