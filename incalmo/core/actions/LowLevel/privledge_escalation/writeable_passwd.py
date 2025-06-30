import asyncio
from incalmo.core.actions.low_level_action import LowLevelAction
from incalmo.core.models.attacker.agent import Agent
from incalmo.core.models.events import Event
from incalmo.models.command_result import CommandResult


class WriteablePasswdExploit(LowLevelAction):
    def __init__(self, agent: Agent):
        command = "./writeable_passwd.sh"
        payloads = ["downloadAgent.sh", "writeable_passwd.sh"]
        super().__init__(agent, command, payloads, command_delay=3)

    async def get_result(
        self,
        result: CommandResult,
    ) -> list[Event]:
        # sleep to allow for the agent to get to the new host
        await asyncio.sleep(10)
        return []
