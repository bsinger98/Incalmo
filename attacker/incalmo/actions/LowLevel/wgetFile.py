from ..low_level_action import LowLevelAction

from models.attacker.agent import Agent


class wgetFile(LowLevelAction):
    def __init__(self, agent: Agent, url: str):
        self.url = url
        command = f"wget -P ~/ {url}"
        super().__init__(agent, command)
