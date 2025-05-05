from ..LowLevelAction import LowLevelAction

from app.objects.c_agent import Agent


class WriteFile(LowLevelAction):
    ability_name = "deception-writefile"

    def __init__(self, agent: Agent, file_path: str, file_contents: str):
        facts = {"host.file.path": file_path}
        super().__init__(agent, facts, WriteFile.ability_name)
        self.file_path = file_path
        self.file_contents = file_contents
