from incalmo.models.events import Event
from incalmo.models.network import Host

class ExfiltratedData(Event):
    def __init__(
        self,
        file: str,
        hash: str
    ):
        self.file = file
        self.hash = hash

    def __str__(self):
        return f"ExfiltratedData: {self.file} with hash {self.hash}"
