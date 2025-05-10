from ..low_level_action import LowLevelAction
from models.attacker.agent import Agent

from models.events import Event, FileContentsFound


class ReadFile(LowLevelAction):
    ability_name = "deception-readfile"

    def __init__(self, agent: Agent, file_path: str):
        self.file_path = file_path
        command = f"cat {file_path}"
        super().__init__(agent, command)

    async def get_result(
        self,
        stdout: str | None,
        stderr: str | None,
    ) -> list[Event]:
        if stdout is None:
            return []

        return [FileContentsFound(self.file_path, stdout)]
