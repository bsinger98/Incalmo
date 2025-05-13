from typing import List
from ..low_level_action import LowLevelAction
from incalmo.models.attacker.agent import Agent
from incalmo.models.events import Event, ServicesDiscoveredOnHost
from models.command_result import CommandResult

import xml.etree.ElementTree as ET


# TODO FIX THIS
class ScanHost(LowLevelAction):
    ability_name = "deception-nmap"
    host: str

    def __init__(self, agent: Agent, host_ip: str):
        self.host = host_ip
        command = f"nmap -sV --version-light -oX - {host_ip}"

        super().__init__(agent, command)

    async def get_result(
        self,
        result: CommandResult,
    ) -> list[Event]:
        if result.output is None:
            return []

        tree = ET.parse(result.output)
        root = tree.getroot()
        services_by_host = {}
        # Iterate over each <host> element
        for host in root.findall("host"):
            # Grab the first IPv4 or IPv6 address we find
            addr_elem = host.find("address")
            if addr_elem is None:
                continue
            ip = addr_elem.get("addr")

            services: List[str] = []
            ports = host.find("ports")
            if ports is not None:
                # For each <port>, check if state is "open" then record the service name
                for port in ports.findall("port"):
                    state = port.find("state")
                    if state is not None and state.get("state") == "open":
                        svc = port.find("service")
                        if svc is not None and svc.get("name"):
                            services.append(svc.get("name"))

            services_by_host[ip] = services

        return services_by_host
