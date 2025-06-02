from ..low_level_action import LowLevelAction

from incalmo.core.models.attacker.agent import Agent


class CopyFile(LowLevelAction):
    def __init__(self, agent: Agent, source_path: str, destination_path: str):
        self.source_path = source_path
        self.destination_path = destination_path

        command = f"cp {source_path} {destination_path}"
        super().__init__(agent, command)
