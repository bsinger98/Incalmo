from ..low_level_action import LowLevelAction
from models.attacker.agent import Agent
from models.events import Event, BashOutputEvent


class RunBashCommand(LowLevelAction):
    def __init__(self, agent: Agent, command: str):
        super().__init__(agent, command)

    async def get_result(
        self,
        stdout: str | None,
        stderr: str | None,
    ) -> list[Event]:
        if stdout is None or stderr is None:
            return []

        if stderr:
            return [BashOutputEvent(self.agent, stderr)]

        return [BashOutputEvent(self.agent, stdout)]
