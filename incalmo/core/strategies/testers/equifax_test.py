from incalmo.core.strategies.perry_strategy import PerryStrategy
from incalmo.core.actions.LowLevel import RunBashCommand, ScanHost
from incalmo.core.actions.HighLevel import (
    Scan,
    FindInformationOnAHost,
    LateralMoveToHost,
)
from incalmo.core.models.network import Host, Subnet


class EquifaxStrategy(PerryStrategy):
    async def step(self) -> bool:
        agents = self.environment_state_service.get_agents()
        # Scan Action
        print(
            f"[DEBUG] Environment Service Before Scan: {self.environment_state_service}"
        )
        host = Host(ip_address="192.168.199.10", agents=agents)
        events = await self.high_level_action_orchestrator.run_action(
            Scan(
                host,
                [
                    Subnet(ip_mask="192.168.199.0/24", hosts=[host]),
                    Subnet(ip_mask="192.168.200.0/24", hosts=[]),
                    Subnet(ip_mask="192.168.201.0/24", hosts=[]),
                ],
            )
        )
        # Lateral Move Action
        print(f"[DEBUG] Lateral Move:")
        current_host = self.environment_state_service.network.find_host_by_ip(
            "192.168.199.10"
        )
        print(f"[DEBUG] Current host: {str(current_host)}")
        target_host = self.environment_state_service.network.find_host_by_ip(
            "192.168.200.20"
        )
        print(f"[DEBUG] Target host: {str(target_host)}")
        events += await self.high_level_action_orchestrator.run_action(
            LateralMoveToHost(
                target_host,
                current_host,
            )
        )
        # Find Information On Host Action

        print(f"[DEBUG] Finding information on host:")
        # Target hosts
        target_ips = ["192.168.200.20"]

        for ip in target_ips:
            target_host = self.environment_state_service.network.find_host_by_ip(ip)
            print(f"[DEBUG] Target host: {str(target_host)}")
            events = await self.high_level_action_orchestrator.run_action(
                FindInformationOnAHost(target_host)
            )
        for event in events:
            print(event)
        print(
            f"[DEBUG] Environment Service After Scan: {self.environment_state_service}"
        )
        return True
