from incalmo.models.events import Event
from incalmo.models.network import Host

from incalmo.models.attacker.agent import Agent


class CriticalDataFound(Event):
    def __init__(self, host: Host, agent: Agent, files_paths: list[str]):
        self.host: Host = host
        self.agent: Agent = agent
        self.files = files_paths

    def __str__(self):
        return f"CriticalDataFound: {self.host} - {self.files}"
