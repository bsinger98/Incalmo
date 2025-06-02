from incalmo.core.models.events import Event
from incalmo.core.models.attacker.agent import Agent


class RootAccessOnHost(Event):
    def __init__(
        self,
        root_agent: Agent,
    ):
        self.root_agent = root_agent

    def __str__(self):
        return f"RootAccessOnHost: {self.root_agent.hostname}"
