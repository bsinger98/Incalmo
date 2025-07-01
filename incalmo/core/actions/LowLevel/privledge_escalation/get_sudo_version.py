import re

from incalmo.models.command_result import CommandResult
from incalmo.core.actions.low_level_action import LowLevelAction
from incalmo.core.models.attacker.agent import Agent

from incalmo.core.models.events import Event, SudoVersion


class GetSudoVersion(LowLevelAction):
    def __init__(self, agent: Agent):
        command = "sudo -V"
        self.command = command

        super().__init__(agent, command)

    async def get_result(
        self,
        result: CommandResult,
    ) -> list[Event]:
        if result is None:
            return []

        output = result.output
        # Regular expression to match version numbers
        version_pattern = re.compile(r"version\s([\d.]+p?\d*)")
        # Find and check all version numbers
        versions = version_pattern.findall(output)
        for version in versions:
            pattern = r"^(\d+)\.(\d+)\.(\d+)(?:p(\d+))?$"
            match = re.match(pattern, version)
            if match:
                return [SudoVersion(self.agent, version)]

        return []
