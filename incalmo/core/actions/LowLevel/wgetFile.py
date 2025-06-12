from ..low_level_action import LowLevelAction

from incalmo.core.models.attacker.agent import Agent


class wgetFile(LowLevelAction):
    def __init__(self, agent: Agent, url: str, high_level_action_id: str):
        self.url = url

        command = f"wget -P ~/ {url}"
        super().__init__(agent, command, high_level_action_id=high_level_action_id)
