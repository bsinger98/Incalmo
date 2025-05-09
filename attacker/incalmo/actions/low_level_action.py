from abc import ABC, abstractmethod

from incalmo.models.events.Event import Event
from incalmo.models.attacker.agent import Agent


class LowLevelAction(ABC):
    def __init__(
        self,
        agent: Agent,
        command: str,
        payloads: list[str] | None = None,
    ):
        self.agent = agent
        self.command = command
        self.payloads = payloads if payloads is not None else []

    def __str__(self):
      params = ", ".join(f"{key}={repr(value)}" for key, value in self.__dict__.items())
      return f"{self.__class__.__name__}: {params}"
    
    @abstractmethod
    async def get_result(
        self,
        stdout: str | None,
        stderr: str | None,
    ) -> list[Event]:
        return []
