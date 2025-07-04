from incalmo.core.models.events import Event


class FileContentsFound(Event):
    def __init__(self, file: str, contents: str):
        self.file = file
        self.contents = contents

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: path={self.file}, contents={self.contents}"
