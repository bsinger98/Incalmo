from ..low_level_action import LowLevelAction
from models.attacker.agent import Agent


class WriteFile(LowLevelAction):
    def __init__(self, agent: Agent, file_path: str, file_contents: str):
        self.file_path = file_path
        self.file_contents = file_contents
        command = f'echo "{file_contents}" >> {file_path}'
        super().__init__(agent, command)
