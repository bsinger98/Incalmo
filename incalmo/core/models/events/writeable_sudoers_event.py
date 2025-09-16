from incalmo.core.models.events import Event
from incalmo.models.agent import Agent


class WriteablePasswd(Event):
    def __init__(self, agent: Agent):
        self.agent = agent

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.agent.hostname}"
