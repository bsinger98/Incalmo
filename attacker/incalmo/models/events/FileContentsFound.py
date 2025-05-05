from plugins.deception.app.models.events import Event
from app.objects.c_agent import Agent


class FileContentsFound(Event):
    def __init__(self, file: str, contents: str):
        self.file = file
        self.contents = contents

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: path={self.file}, contents={self.contents}"
