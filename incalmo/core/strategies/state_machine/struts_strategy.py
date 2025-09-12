from incalmo.core.strategies.incalmo_strategy import IncalmoStrategy
from incalmo.core.actions.LowLevel import RunBashCommand, ScanHost, ExploitStruts
from incalmo.core.actions.HighLevel.scan import Scan
from incalmo.core.models.network import Host, Subnet


class StrutsStrategy(IncalmoStrategy):
    async def step(self) -> bool:
        agents = self.environment_state_service.get_agents()
        events = await self.low_level_action_orchestrator.run_action(
            ExploitStruts(agents[0], "host.docker.internal", "8080")
        )
        for event in events:
            print(event)
        return True
