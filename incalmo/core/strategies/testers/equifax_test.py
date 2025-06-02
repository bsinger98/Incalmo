from incalmo.core.strategies.perry_strategy import PerryStrategy
from incalmo.core.actions.LowLevel import RunBashCommand, ScanHost
from incalmo.core.actions.HighLevel import (
    Scan,
    FindInformationOnAHost,
    LateralMoveToHost,
)
from incalmo.core.models.network import Host, Subnet


class EquifaxStrategy(PerryStrategy, name="equifax_strategy"):
    async def step(self) -> bool:
        agents = self.environment_state_service.get_agents()
        for agent in agents:
            print(f"[DEBUG] Agents at start of exploit: {str(agent)}")
        # Initial Scan Action
        print(
            f"[DEBUG] Environment Service Before Test: {self.environment_state_service}"
        )

        hosts = self.environment_state_service.network.get_all_hosts()
        for _host in hosts:
            print(f"[DEBUG] Initial host: {str(_host)}")
            host = _host
        events = await self.high_level_action_orchestrator.run_action(
            Scan(
                host,
                [
                    Subnet(ip_mask="192.168.199.0/24", hosts=[host]),
                    Subnet(ip_mask="192.168.200.0/24", hosts=[]),
                ],
            )
        )
        print("[DEBUG] Initial Scan Action Events:")
        for event in events:
            print(event)
        agents = self.environment_state_service.get_agents()
        self.environment_state_service.update_host_agents(agents)
        print(
            f"[DEBUG] Environment Service After Scan: {self.environment_state_service}"
        )

        return True

        # Lateral Move Action to Webserver
        print(f"[DEBUG] Lateral Move to Webserver:")
        agents = self.environment_state_service.get_agents()
        for agent in agents:
            print(f"[DEBUG] Agents before Lateral Move to Webserver: {str(agent)}")
        host_candidates = ["192.168.200.10", "192.168.199.10"]
        current_host = None
        for ip in host_candidates:
            host = self.environment_state_service.network.find_host_by_ip(ip)
            if host and getattr(host, "agents", []):
                current_host = host
                break
        print(f"[DEBUG] Current host: {str(current_host)}")
        target_host = self.environment_state_service.network.find_host_by_ip(
            "192.168.200.20"
        )
        print(f"[DEBUG] Target host: {str(target_host)}")
        events = await self.high_level_action_orchestrator.run_action(
            LateralMoveToHost(
                target_host,
                current_host,
            )
        )
        print("[DEBUG] Lateral Move Action Events:")
        for event in events:
            print(event)
        agents = self.environment_state_service.get_agents()
        self.environment_state_service.update_host_agents(agents)

        # Find Information On Host Action
        print(f"[DEBUG] Finding information on host:")
        agents = self.environment_state_service.get_agents()
        for agent in agents:
            print(f"[DEBUG] Agents before Finding Information: {str(agent)}")
        # Target hosts
        target_ips = ["192.168.200.20", "192.168.201.20"]

        for ip in target_ips:
            target_host = self.environment_state_service.network.find_host_by_ip(ip)
            if target_host is not None:
                print(f"[DEBUG] Target host: {str(target_host)} of ip {ip}")
                events = await self.high_level_action_orchestrator.run_action(
                    FindInformationOnAHost(target_host)
                )
        for event in events:
            print(event)

        # Lateral Move to database
        agents = self.environment_state_service.get_agents()
        self.environment_state_service.update_host_agents(agents)
        print(f"[DEBUG] Lateral Move to Database:")
        agents = self.environment_state_service.get_agents()
        for agent in agents:
            print(f"[DEBUG] Agents before Lateral Move to Database: {str(agent)}")
        host_candidates = ["192.168.200.20", "192.168.201.20"]
        current_host = None
        for ip in host_candidates:
            host = self.environment_state_service.network.find_host_by_ip(ip)
            if host and getattr(host, "agents", []):
                current_host = host
                break
        print(f"[DEBUG] Current host: {str(current_host)}")
        target_host = self.environment_state_service.network.find_host_by_ip(
            "192.168.201.100"
        )
        print(f"[DEBUG] Target host: {str(target_host)}")
        events = await self.high_level_action_orchestrator.run_action(
            LateralMoveToHost(
                target_host,
                current_host,
            )
        )
        for event in events:
            print(event)
        agents = self.environment_state_service.get_agents()
        for agent in agents:
            print(f"[DEBUG] Agents after Lateral Move to Database: {str(agent)}")

        print(
            f"[DEBUG] Environment Service After Test: {self.environment_state_service}"
        )
        for i in range(10):
            agents = self.environment_state_service.get_agents()
            self.environment_state_service.update_host_agents(agents)
        for agent in agents:
            print(f"[DEBUG] Agents at end: {str(agent)}")
        return True
