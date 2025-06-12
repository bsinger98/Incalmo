from ..low_level_action import LowLevelAction
from incalmo.core.models.attacker.agent import Agent


class WriteFile(LowLevelAction):
    def __init__(
        self,
        agent: Agent,
        file_path: str,
        file_contents: str,
        high_level_action_id: str,
    ):
        self.file_path = file_path
        self.file_contents = file_contents
        command = f'echo "{file_contents}" >> {file_path}'
        super().__init__(agent, command, high_level_action_id=high_level_action_id)
