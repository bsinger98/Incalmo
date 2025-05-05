from plugins.deception.app.models.events import Event


class VulnerableServiceFound(Event):
    def __init__(
        self,
        port: int,
        host: str,
        service: str,
        cve: str,
    ):
        self.port = port
        self.host = host
        self.service = service
        self.cve = cve

    def __str__(self):
        return f"VulnerableServiceFound: {self.host} - {self.service} - {self.port} - {self.cve}"
