from incalmo.models.command_result import CommandResult
from incalmo.core.actions.low_level_action import LowLevelAction
from incalmo.core.models.attacker.agent import Agent
from incalmo.core.models.events import Event, WriteablePasswd


class CheckPasswdPermissions(LowLevelAction):
    def __init__(self, agent: Agent):
        command = "ls -l /etc/passwd"
        self.command = command
        super().__init__(agent, command)

    async def get_result(
        self,
        result: CommandResult,
    ) -> list[Event]:
        if result is None:
            return []

        output = result.output
        permissions = output.split(" ")[0]

        # Check if the permissions string contains 2 or more "w" characters
        if permissions.count("w") >= 2:
            return [WriteablePasswd(self.agent)]

        return []
