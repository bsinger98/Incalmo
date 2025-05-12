from ..low_level_action import LowLevelAction
from incalmo.models.attacker.agent import Agent
from incalmo.models.events import Event, ExfiltratedData
from models.command_result import CommandResult
import os


class MD5SumAttackerData(LowLevelAction):
    ability_name = "deception-exfil-results"

    def __init__(self, agent: Agent):
        command = "find ~/ -maxdepth 1 -type f -exec md5sum {} +"
        super().__init__(agent, command)

    async def get_result(
        self,
        result: CommandResult,
    ) -> list[Event]:
        if result.output is None:
            return []

        lines = result.output.split("\n")
        events = []

        for line in lines:
            if line == "":
                continue
            elif "data" in line:
                file_hash = line.split()[0]
                filename = line.split()[1]
                filename = os.path.basename(filename)
                events.append(ExfiltratedData(filename, file_hash))

        return events
