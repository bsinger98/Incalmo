from incalmo.strategies.perry_strategy import PerryStrategy
from incalmo.actions.LowLevel import RunBashCommand, ScanHost
from incalmo.actions.HighLevel.Scan import Scan
from incalmo.models.network import Host, Subnet


class DebugStrategy(PerryStrategy):
    async def step(self) -> bool:
        agents = self.environment_state_service.get_agents()
        # events = await self.low_level_action_orchestrator.run_action(
        #     RunBashCommand(agents[0], "ls")
        # )
        # events = await self.low_level_action_orchestrator.run_action(
        #     ScanHost(agents[0], "localhost")
        # )
        host = Host(ip_address="localhost", agents=agents)
        events = await self.high_level_action_orchestrator.run_action(
            Scan(
                host,
                [Subnet(ip_mask="127.0.0.1/32", hosts=[host])],
            )
        )
        for event in events:
            print(event)
        return True
