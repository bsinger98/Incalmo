from incalmo.core.models.events import Event, InfectedNewHost
from incalmo.core.models.network import Host
from incalmo.core.services import (
    LowLevelActionOrchestrator,
    EnvironmentStateService,
    AttackGraphService,
)
from incalmo.core.services.action_context import Context

from ..high_level_action import HighLevelAction
from ..LowLevel import ExploitStruts, SSHLateralMove, NCLateralMove


class LateralMoveToHost(HighLevelAction):
    def __init__(
        self,
        host_to_attack: Host,
        attacking_host: Host,
        stop_after_success: bool = True,
    ):
        super().__init__()
        self.host_to_attack = host_to_attack
        self.attacking_host = attacking_host
        self.stop_after_success = stop_after_success

    async def run(
        self,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
        context: Context,
    ) -> list[Event]:
        """
        _random_lateral_move
        @brief: randomly chooses a host to attack and randomly chooses a port to attack on that host.
                Then, it sets up the lateral move link and runs it.
        """
        events = []

        # Check if attacking host has credentials
        if len(self.attacking_host.ssh_config) > 0:
            for cred in self.attacking_host.ssh_config:
                if cred.host_ip in self.host_to_attack.ip_addresses:
                    agent = cred.agent_discovered
                    new_events = await low_level_action_orchestrator.run_action(
                        SSHLateralMove(agent, cred.hostname), context
                    )
                    for event in new_events:
                        if type(event) is InfectedNewHost:
                            event.credential_used = cred

                    if len(new_events) > 0:
                        if self.stop_after_success:
                            return new_events
                        else:
                            events += new_events

        # Try to exploit a service
        agent = self.attacking_host.get_agent()
        if not agent:
            return events

        for (
            port_to_attack,
            service_to_attack,
        ) in self.host_to_attack.open_ports.items():
            action_to_run = None

            if (
                "CVE-2017-5638" in service_to_attack.CVE
                and self.host_to_attack.has_an_ip_address()
            ):
                action_to_run = ExploitStruts(
                    agent,
                    self.host_to_attack.get_ip_address(),
                    str(port_to_attack),
                )
            elif port_to_attack == 4444 and self.host_to_attack.has_an_ip_address():
                action_to_run = NCLateralMove(
                    agent,
                    self.host_to_attack.get_ip_address(),
                    str(port_to_attack),
                )

            if action_to_run is None:
                continue

            new_events = await low_level_action_orchestrator.run_action(
                action_to_run, context
            )

            if len(new_events) > 0:
                if self.stop_after_success:
                    return new_events
                else:
                    events += new_events

        return events
