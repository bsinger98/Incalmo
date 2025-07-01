import asyncio

from incalmo.models.command_result import CommandResult
from incalmo.core.actions.low_level_action import LowLevelAction
from incalmo.core.models.attacker.agent import Agent

from incalmo.core.models.events import Event


class SudoBaronExploit(LowLevelAction):
    def __init__(self, agent: Agent):
        command = "python3 sudo_baron_exploit.py"
        payloads = ["sudo_baron_exploit.py"]
        super().__init__(agent, command, payloads)

    async def get_result(
        self,
        result: CommandResult,
    ) -> list[Event]:
        # sleep to allow for the agent to get to the new host
        await asyncio.sleep(10)
        return []
