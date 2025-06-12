from ..low_level_action import LowLevelAction
from incalmo.core.models.events import Event, FilesFound

from incalmo.core.models.attacker.agent import Agent
from incalmo.models.command_result import CommandResult


class ListFilesInDirectory(LowLevelAction):
    def __init__(self, agent: Agent, dir_path: str, high_level_action_id: str):
        self.dir_path = dir_path

        command = f"ls -l {dir_path}"

        super().__init__(agent, command, high_level_action_id=high_level_action_id)

    async def get_result(
        self,
        result: CommandResult,
    ) -> list[Event]:
        if result.output is None:
            return []

        # Parse the output
        lines = result.output.splitlines()
        files = []
        for line in lines:
            parts = line.split()
            if len(parts) > 8:
                file_name = parts[-1]
                files.append(file_name)

        return [FilesFound(self.agent, files)]
