from ..low_level_action import LowLevelAction

from incalmo.models.agent import Agent


class wgetFile(LowLevelAction):
    def __init__(self, agent: Agent, url: str):
        self.url = url

        command = f"wget -P ~/ {url}"
        super().__init__(agent, command)
