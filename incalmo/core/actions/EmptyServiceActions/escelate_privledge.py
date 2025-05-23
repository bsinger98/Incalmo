from incalmo.core.actions.high_level_action import HighLevelAction
from incalmo.core.actions.HighLevel.escelate_privledge import EscelatePrivledge
from incalmo.core.services import EnvironmentStateService


class EscelatePrivledgeWrapper:
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

        return EscelatePrivledge(host)
