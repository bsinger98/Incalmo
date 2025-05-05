from plugins.deception.app.models.events import Event
from plugins.deception.app.models.network import Host

from app.objects.c_agent import Agent


class CriticalDataFound(Event):
    def __init__(self, host: Host, agent: Agent, files_paths: list[str]):
        self.host: Host = host
        self.agent: Agent = agent
        self.files = files_paths

    def __str__(self):
        return f"CriticalDataFound: {self.host} - {self.files}"
