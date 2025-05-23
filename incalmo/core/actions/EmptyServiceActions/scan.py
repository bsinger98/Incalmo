from incalmo.core.actions.high_level_action import HighLevelAction
from incalmo.core.actions.HighLevel.Scan import Scan
from incalmo.core.services import EnvironmentStateService
from incalmo.core.models.network import Subnet


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
