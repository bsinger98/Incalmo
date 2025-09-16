from typing import List
from ..low_level_action import LowLevelAction
from incalmo.models.agent import Agent
from incalmo.core.models.events import Event, ServicesDiscoveredOnHost
from incalmo.models.command_result import CommandResult

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
                        portid = port.get("portid")
                        if svc is not None and svc.get("name") and portid:
                            port_num = int(portid)
                            service_name = svc.get("name")

                            if service_name:  # Make sure service_name is not None
                                # Check if service uses SSL/TLS
                                tunnel = svc.get("tunnel")
                                if tunnel == "ssl":
                                    service_name += "+ssl"  # Mark SSL services

                                services[port_num] = service_name

            services_by_host[ip] = services

        return [
            ServicesDiscoveredOnHost(ip, services)
            for ip, services in services_by_host.items()
        ]
