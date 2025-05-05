import re

from plugins.deception.app.actions.HighLevelAction import HighLevelAction
from plugins.deception.app.actions.HighLevel import Scan
from plugins.deception.app.services import EnvironmentStateService
from plugins.deception.app.models.network import Subnet


class ScanWrapper:
    def __init__(self, scan_host_ip: str, ip_to_scan: str):
        self.scan_host_ip = scan_host_ip
        self.ip_to_scan = ip_to_scan

    def convert(
        self,
        environment_state_service: EnvironmentStateService,
    ) -> HighLevelAction | None:
        # Get host
        host = environment_state_service.network.find_host_by_ip(self.scan_host_ip)
        if host is None:
            return None

        subnet = Subnet(self.ip_to_scan)
        return Scan(host, [subnet])
