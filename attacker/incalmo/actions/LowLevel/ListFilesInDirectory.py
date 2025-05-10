from ..low_level_action import LowLevelAction
from models.events import Event, FilesFound

from models.attacker.agent import Agent


class ListFilesInDirectory(LowLevelAction):
    def __init__(self, agent: Agent, dir_path: str):
        self.dir_path = dir_path

        command = f"ls -l {dir_path}"

        super().__init__(agent, command)

    async def get_result(
        self,
        stdout: str | None,
        stderr: str | None,
    ) -> list[Event]:
        if stdout is None:
            return []

        # Parse the output
        lines = stdout.splitlines()
        files = []
        for line in lines:
            parts = line.split()
            if len(parts) > 8:
                file_name = parts[-1]
                files.append(file_name)

        return [FilesFound(self.agent, files)]
