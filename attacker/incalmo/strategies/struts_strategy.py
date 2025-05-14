from incalmo.strategies.perry_strategy import PerryStrategy
from incalmo.actions.LowLevel import RunBashCommand, ScanHost, ExploitStruts
from incalmo.actions.HighLevel.Scan import Scan
from incalmo.models.network import Host, Subnet


class StrutsStrategy(PerryStrategy):
    async def step(self) -> bool:
        agents = self.environment_state_service.get_agents()
        events = await self.low_level_action_orchestrator.run_action(
            ExploitStruts(agents[0], "192.168.200.10", "8080")
        )
        for event in events:
            print(event)
        return True
