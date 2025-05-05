import re

from plugins.deception.app.actions.HighLevelAction import HighLevelAction
from plugins.deception.app.actions.HighLevel import LateralMoveToHost
from plugins.deception.app.services import EnvironmentStateService


class LateralMoveToHostWrapper:
    def __init__(self, source_ip_address: str, target_ip_address: str):
        self.source_ip_address = source_ip_address
        self.target_ip_address = target_ip_address

    def convert(
        self,
        environment_state_service: EnvironmentStateService,
    ) -> HighLevelAction | None:
        # Get host
        source_host = environment_state_service.network.find_host_by_ip(
            self.source_ip_address
        )
        target_host = environment_state_service.network.find_host_by_ip(
            self.target_ip_address
        )

        if source_host is None or target_host is None:
            return None

        return LateralMoveToHost(source_host, target_host)
