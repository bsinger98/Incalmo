from incalmo.models.events import Event
from incalmo.models.attacker.agent import Agent


class SudoVersion(Event):
    def __init__(self, agent: Agent, version: str):
        self.agent = agent
        self.version = version

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.agent.host} : {self.version}"
