from incalmo.strategies.perry_strategy import PerryStrategy
from incalmo.actions.LowLevel import RunBashCommand


class DebugStrategy(PerryStrategy):
    async def step(self) -> bool:
        agents = self.environment_state_service.get_agents()
        events = await self.low_level_action_orchestrator.run_action(
            RunBashCommand(agents[0], "ls")
        )
        return True
