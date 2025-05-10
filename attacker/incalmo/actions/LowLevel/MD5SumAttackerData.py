from ..low_level_action import LowLevelAction
from models.attacker.agent import Agent
from models.events import Event, ExfiltratedData
import os


class MD5SumAttackerData(LowLevelAction):
    ability_name = "deception-exfil-results"

    def __init__(self, agent: Agent):
        command = "find ~/ -maxdepth 1 -type f -exec md5sum {} +"
        super().__init__(agent, command)

    async def get_result(
        self,
        stdout: str | None,
        stderr: str | None,
    ) -> list[Event]:
        if stdout is None:
            return []

        lines = stdout.split("\n")
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
