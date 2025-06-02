from abc import ABC, abstractmethod

from incalmo.core.models.events.Event import Event
from incalmo.models.command_result import CommandResult
from incalmo.core.models.attacker.agent import Agent


class LowLevelAction(ABC):
    def __init__(
        self,
        agent: Agent,
        command: str,
        payloads: list[str] | None = None,
        command_delay: int = 0,
    ):
        self.agent = agent
        self.command = command
        self.payloads = payloads if payloads is not None else []
        self.command_delay = command_delay

    def __str__(self):
        def format_value(value):
            if isinstance(value, list):
                return "[" + ", ".join(str(v) for v in value) + "]"
            return str(value)

        params = ", ".join(
            f"{key}={repr(format_value(value))}" for key, value in self.__dict__.items()
        )
        return f"{self.__class__.__name__}: {params}"

    async def get_result(
        self,
        results: CommandResult,
    ) -> list[Event]:
        return []
