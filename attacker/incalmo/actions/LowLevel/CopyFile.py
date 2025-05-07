from ..low_level_action import LowLevelAction

from models.attacker.agent import Agent


class CopyFile(LowLevelAction):
    def __init__(self, agent: Agent, source_path: str, destination_path: str):
        command = f"cp {source_path} {destination_path}"

        super().__init__(agent, command)
