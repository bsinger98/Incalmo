from incalmo.models.events import Event
from incalmo.models.network import Host


class ExfiltratedData(Event):
    def __init__(
        self,
        file: str,
    ):
        self.file = file

    def __str__(self):
        return f"ExfiltratedData: {self.file}"
