from incalmo.core.strategies.incalmo_strategy import IncalmoStrategy
from incalmo.core.actions.LowLevel import (
    RunBashCommand,
    ScanHost,
    RunMetasploitBindFile,
)
from incalmo.core.actions.HighLevel import (
    Scan,
    FindInformationOnAHost,
    LateralMoveToHost,
    ExfiltrateData,
)
from incalmo.core.models.network import Host, Subnet


class MetasploitStrategy(IncalmoStrategy):
    async def step(self) -> bool:
        agents = self.environment_state_service.get_agents()
        hosts = self.environment_state_service.network.get_all_hosts()
        attack_host = hosts[0]

        events = await self.high_level_action_orchestrator.run_action(
            Scan(
                attack_host,
                [
                    Subnet(ip_mask="192.168.199.0/24", hosts=[attack_host]),
                    Subnet(ip_mask="192.168.200.0/24", hosts=[]),
                ],
            )
        )
        print("Scan results:")
        for event in events:
            print(f"{str(event)}")

        agents = self.environment_state_service.get_agents()
        self.environment_state_service.update_host_agents(agents)

        webserver1 = self.environment_state_service.network.find_host_by_ip(
            "192.168.199.20"
        )

        if not webserver1:
            print("Webserver not found in network state.")
            return False
        events = await self.high_level_action_orchestrator.run_action(
            LateralMoveToHost(webserver1, attack_host)
        )
        print("Lateral move to webserver1 results:")
        for event in events:
            print(event)

        agents = self.environment_state_service.get_agents()
        self.environment_state_service.update_host_agents(agents)

        print(f"[DEBUG] Current environment state: {self.environment_state_service}")
        webserver1 = self.environment_state_service.network.find_host_by_ip(
            "192.168.199.20"
        )
        if not webserver1:
            print("Webserver not found in network state after lateral move.")
            return False
        events = await self.low_level_action_orchestrator.run_action(
            RunMetasploitBindFile(webserver1.agents[0])
        )
        print("Metasploit bind file results:")
        for event in events:
            print(event)

        return True
