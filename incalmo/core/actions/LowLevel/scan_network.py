from ..low_level_action import LowLevelAction

from incalmo.models.agent import Agent
from incalmo.core.models.events import Event, HostsDiscovered
from incalmo.models.command_result import CommandResult
from incalmo.core.services.config_service import ConfigService

import xml.etree.ElementTree as ET


class ScanNetwork(LowLevelAction):
    def __init__(self, agent: Agent, subnet_mask: str):
        self.subnet_mask = subnet_mask
        self.blacklist_ips = ConfigService().get_config().blacklist_ips
        exclude_option = ""
        if self.blacklist_ips and len(self.blacklist_ips) > 0:
            exclude_option = f"--exclude {','.join(self.blacklist_ips)}"

        command = (
            f"nmap --max-rtt-timeout 100ms -sn {exclude_option} -oX - {subnet_mask}"
        )

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
