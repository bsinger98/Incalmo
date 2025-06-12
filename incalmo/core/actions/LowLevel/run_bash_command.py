from ..low_level_action import LowLevelAction
from incalmo.core.models.attacker.agent import Agent
from incalmo.core.models.events import Event, BashOutputEvent
from incalmo.models.command_result import CommandResult


class RunBashCommand(LowLevelAction):
    def __init__(self, agent: Agent, command: str, high_level_action_id: str):
        super().__init__(agent, command, high_level_action_id=high_level_action_id)

    async def get_result(
        self,
        result: CommandResult,
    ) -> list[Event]:
        if result.output is None or result.stderr is None:
            return []

        if result.stderr:
            return [BashOutputEvent(self.agent, result.stderr)]

        return [BashOutputEvent(self.agent, result.output)]
