from plugins.deception.app.models.events import Event
from app.objects.c_agent import Agent


class FilesFound(Event):
    def __init__(self, agent: Agent, files: list[str]):
        self.agent = agent
        self.files = files

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.files}"
