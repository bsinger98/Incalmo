from plugins.deception.app.models.events import Event


class ServicesDiscoveredOnHost(Event):
    def __init__(self, host_ip: str, services: dict[int, str]):
        self.host_ip = host_ip
        self.services = services

    def __str__(self):
        return f"ServicesDiscoveredOnHost: {self.host_ip} - {self.services}"
