from incalmo.models.events import Event
from incalmo.models.attacker.agent import Agent


class BashOutputEvent(Event):
    def __init__(self, agent: Agent, results: str):
        self.agent = agent
        self.bash_output = results

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.bash_output}"
