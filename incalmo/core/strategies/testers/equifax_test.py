from incalmo.core.strategies.incalmo_strategy import IncalmoStrategy
from incalmo.core.actions.LowLevel import RunBashCommand, ScanHost
from incalmo.core.actions.HighLevel import (
    Scan,
    FindInformationOnAHost,
    LateralMoveToHost,
    ExfiltrateData,
)
from incalmo.core.models.network import Host, Subnet


class EquifaxStrategy(IncalmoStrategy, name="equifax_strategy"):
    async def step(self) -> bool:
        agents = self.environment_state_service.get_agents()
        hosts = self.environment_state_service.network.get_all_hosts()
        host = hosts[0]

        events = await self.high_level_action_orchestrator.run_action(
            Scan(
                host,
                [
                    Subnet(ip_mask="192.168.199.0/24", hosts=[host]),
                    Subnet(ip_mask="192.168.200.0/24", hosts=[]),
                ],
            )
        )
        agents = self.environment_state_service.get_agents()
        self.environment_state_service.update_host_agents(agents)

        host_candidates = ["192.168.200.10", "192.168.199.10"]
        current_host = None
        for ip in host_candidates:
            host = self.environment_state_service.network.find_host_by_ip(ip)
            if host and getattr(host, "agents", []):
                current_host = host
                break
        database = self.environment_state_service.network.find_host_by_ip(
            "192.168.200.20"
        )

        events = await self.high_level_action_orchestrator.run_action(
            LateralMoveToHost(
                database,
                current_host,
            )
        )
        agents = self.environment_state_service.get_agents()
        self.environment_state_service.update_host_agents(agents)

        # Target hosts
        target_ips = ["192.168.200.20", "192.168.201.20"]

        for ip in target_ips:
            database = self.environment_state_service.network.find_host_by_ip(ip)
            if database is not None:
                events = await self.high_level_action_orchestrator.run_action(
                    FindInformationOnAHost(database)
                )

        # Lateral Move to database
        agents = self.environment_state_service.get_agents()
        self.environment_state_service.update_host_agents(agents)

        host_candidates = ["192.168.200.20", "192.168.201.20"]
        current_host = None
        for ip in host_candidates:
            host = self.environment_state_service.network.find_host_by_ip(ip)
            if host and getattr(host, "agents", []):
                current_host = host
                break
        database = self.environment_state_service.network.find_host_by_ip(
            "192.168.201.100"
        )
        events = await self.high_level_action_orchestrator.run_action(
            LateralMoveToHost(
                database,
                current_host,
            )
        )
        # Current agents
        print("Current agents:")
        for agent in self.environment_state_service.get_agents():
            print(f"{str(agent)}")

        print("Database:")
        print(database)

        print("Env state service hosts:")
        for host in self.environment_state_service.network.get_all_hosts():
            print(f"{str(host)}")

        # Find information on database
        events = await self.high_level_action_orchestrator.run_action(
            FindInformationOnAHost(database)
        )
        print("Finding information on database")
        for event in events:
            print(f"{str(event)}")

        # Exfiltrate data
        events = await self.high_level_action_orchestrator.run_action(
            ExfiltrateData(database)
        )
        print("Exfiltrating data")
        for event in events:
            print(f"{str(event)}")

        return True
