from incalmo.api.server_api import C2ApiClient
from incalmo.models.command_result import CommandResult
from incalmo.core.actions.low_level_action import LowLevelAction
from incalmo.core.models.events import Event
from incalmo.core.services.low_level_action_orchestrator import (
    LowLevelActionOrchestrator,
)
import asyncio


class WhoamiAction(LowLevelAction):
    async def get_result(self, result: CommandResult) -> list[Event]:
        print(result)
        return []


async def main():
    print("Get agents")
    client = C2ApiClient()
    prior_agents = client.get_agents()
    print("Agents:")
    for agent in prior_agents:
        print(agent.paw)
    action = WhoamiAction(
        agent=prior_agents[0],
        command="ls -l",
        payloads=["dynamic_payloads/test_attack.txt"],
    )
    orchestrator = LowLevelActionOrchestrator()
    events = await orchestrator.run_action(action)


if __name__ == "__main__":
    asyncio.run(main())
