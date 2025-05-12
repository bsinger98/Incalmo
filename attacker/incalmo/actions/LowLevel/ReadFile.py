from ..low_level_action import LowLevelAction
from incalmo.models.attacker.agent import Agent
from models.command_result import CommandResult

from incalmo.models.events import Event, FileContentsFound


class ReadFile(LowLevelAction):
    ability_name = "deception-readfile"

    def __init__(self, agent: Agent, file_path: str):
        self.file_path = file_path
        command = f"cat {file_path}"
        super().__init__(agent, command)

    async def get_result(
        self,
        result: CommandResult,
    ) -> list[Event]:
        if result.output is None:
            return []
        
        return [FileContentsFound(self.file_path, result.output)]