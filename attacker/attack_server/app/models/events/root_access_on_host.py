from plugins.deception.app.models.events import Event
from app.objects.c_agent import Agent
from plugins.deception.app.models.network import SSHCredential


class RootAccessOnHost(Event):
    def __init__(
        self,
        root_agent: Agent,
    ):
        self.root_agent = root_agent

    def __str__(self):
        return f"RootAccessOnHost: {self.root_agent.host}"
