import re

from plugins.deception.app.actions.HighLevelAction import HighLevelAction
from plugins.deception.app.actions.HighLevel import ExfiltrateData
from plugins.deception.app.services import EnvironmentStateService


class ExfiltrateDataWrapper:
    def __init__(self, ip_address: str):
        self.ip_address = ip_address

    def convert(
        self,
        environment_state_service: EnvironmentStateService,
    ) -> HighLevelAction | None:
        # Get host
        host = environment_state_service.network.find_host_by_ip(self.ip_address)
        if host is None:
            return None

        return ExfiltrateData(host)
