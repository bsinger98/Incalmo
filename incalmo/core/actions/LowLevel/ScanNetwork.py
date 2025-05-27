from ..low_level_action import LowLevelAction

from incalmo.core.models.attacker.agent import Agent
from incalmo.core.models.events import Event, HostsDiscovered
from incalmo.models.command_result import CommandResult

import xml.etree.ElementTree as ET


class ScanNetwork(LowLevelAction):
    def __init__(self, agent: Agent, subnet_mask: str):
        self.subnet_mask = subnet_mask
        command = f"nmap --max-rtt-timeout 100ms -sn -oX - {subnet_mask}"

        super().__init__(agent, command)

    async def get_result(
        self,
        result: CommandResult,
    ) -> list[Event]:
        # Parse XML blob
        root = ET.fromstring(result.output)

        ips = self.parse_xml_report(root)
        return [HostsDiscovered(self.subnet_mask, ips)]

    def parse_xml_report(self, root):
        online_ips = []
        # get all ips returned by nmap
        for host in root.findall("host"):
            host_ip = host.find("address").get("addr")
            online_ips.append(host_ip)
        return online_ips
