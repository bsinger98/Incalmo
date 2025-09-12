from incalmo.core.strategies.incalmo_strategy import IncalmoStrategy
from incalmo.core.actions.LowLevel import RunBashCommand, ScanHost
from incalmo.core.actions.HighLevel.scan import Scan
from incalmo.core.models.network import Host, Subnet


class DebugStrategy(IncalmoStrategy):
    async def step(self) -> bool:
        agents = self.environment_state_service.get_agents()
        # events = await self.low_level_action_orchestrator.run_action(
        #     RunBashCommand(agents[0], "ls")
        # )
        # events = await self.low_level_action_orchestrator.run_action(
        #     ScanHost(agents[0], "localhost")
        # )
        print(
            f"[DEBUG] Environment Service Before Scan: {self.environment_state_service}"
        )
        host = Host(ip_address="localhost", agents=agents)
        events = await self.high_level_action_orchestrator.run_action(
            Scan(
                host,
                [
                    Subnet(ip_mask="0.0.0.0/32", hosts=[host]),
                    Subnet(ip_mask="192.168.200.0/24", hosts=[]),
                ],
            )
        )
        print(
            f"[DEBUG] Environment Service After Scan: {self.environment_state_service}"
        )
        for event in events:
            print(event)
        return True
