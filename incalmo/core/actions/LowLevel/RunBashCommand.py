from ..low_level_action import LowLevelAction
from incalmo.core.models.attacker.agent import Agent
from incalmo.core.models.events import Event, BashOutputEvent
from models.command_result import CommandResult


class RunBashCommand(LowLevelAction):
    def __init__(self, agent: Agent, command: str):
        super().__init__(agent, command)

    async def get_result(
        self,
        result: CommandResult,
    ) -> list[Event]:
        if result.output is None or result.stderr is None:
            return []

        if result.stderr:
            return [BashOutputEvent(self.agent, result.stderr)]

        return [BashOutputEvent(self.agent, result.output)]
