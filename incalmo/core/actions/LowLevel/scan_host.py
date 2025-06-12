from typing import List
from ..low_level_action import LowLevelAction
from incalmo.core.models.attacker.agent import Agent
from incalmo.core.models.events import Event, ServicesDiscoveredOnHost
from incalmo.models.command_result import CommandResult

import xml.etree.ElementTree as ET


# TODO FIX THIS
class ScanHost(LowLevelAction):
    ability_name = "deception-nmap"
    host: str

    def __init__(self, agent: Agent, host_ip: str, high_level_action_id: str):
        self.host = host_ip
        command = f"nmap -sV --version-light -oX - {host_ip}"

        super().__init__(agent, command, high_level_action_id=high_level_action_id)

    async def get_result(
        self,
        result: CommandResult,
    ) -> list[Event]:
        if result.output is None:
            return []

        root = ET.fromstring(result.output)

        services_by_host = {}
        # Iterate over each <host> element
        for host in root.findall("host"):
            # Grab the first IPv4 or IPv6 address we find
            addr_elem = host.find("address")
            if addr_elem is None:
                continue
            ip = addr_elem.get("addr")

            services: dict[int, str] = {}
            ports = host.find("ports")
            if ports is not None:
                # For each <port>, check if state is "open" then record the service name
                for port in ports.findall("port"):
                    state = port.find("state")
                    if state is not None and state.get("state") == "open":
                        svc = port.find("service")
                        if svc is not None and svc.get("name"):
                            port_num = int(port.get("portid"))
                            service_name = svc.get("name")
                            services[port_num] = service_name

            services_by_host[ip] = services

        return [
            ServicesDiscoveredOnHost(ip, services)
            for ip, services in services_by_host.items()
        ]
