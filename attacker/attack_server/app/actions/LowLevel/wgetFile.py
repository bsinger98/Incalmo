from ..LowLevelAction import LowLevelAction

from app.objects.c_agent import Agent


class wgetFile(LowLevelAction):
    ability_name = "deception-wget-copy"

    def __init__(self, agent: Agent, url: str):
        facts = {
            "host.data.url": url,
        }
        super().__init__(agent, facts, wgetFile.ability_name)
