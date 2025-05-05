from plugins.deception.app.helpers.logging import log_event

from plugins.deception.app.models.events import Event, InfectedNewHost
from plugins.deception.app.models.network import Host
from plugins.deception.app.services import (
    LowLevelActionOrchestrator,
    EnvironmentStateService,
    AttackGraphService,
)

from ..HighLevelAction import HighLevelAction
from ..LowLevel import ExploitStruts, SSHLateralMove, NCLateralMove


class LateralMoveToHost(HighLevelAction):
    def __init__(
        self,
        host_to_attack: Host,
        attacking_host: Host,
        stop_after_success: bool = True,
    ):
        self.host_to_attack = host_to_attack
        self.attacking_host = attacking_host
        self.stop_after_success = stop_after_success

    async def run(
        self,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
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
                if cred.host_ip == self.host_to_attack.ip_address:
                    agent = cred.agent_discovered
                    log_event(
                        "LATERAL MOVE",
                        f"Agent {agent.paw} has credentials for {self.host_to_attack.ip_address}",
                    )
                    new_events = await low_level_action_orchestrator.run_action(
                        SSHLateralMove(agent, cred.hostname)
                    )
                    for event in new_events:
                        if type(event) is InfectedNewHost:
                            event.credential_used = cred

                    if len(new_events) > 0:
                        if self.stop_after_success:
                            return new_events
                        else:
                            events += new_events
        else:
            agent = self.attacking_host.get_agent()
            if not agent:
                log_event(
                    "LateralMoveToHost",
                    f"No agent found for host {self.attacking_host}",
                )
                return events

            # If no credentials, try to exploit a service
            for (
                port_to_attack,
                service_to_attack,
            ) in self.host_to_attack.open_ports.items():
                agent_info = f"{agent.paw} ({agent.host} - {agent.host_ip_addrs})"
                log_event(
                    "ATTACKING PORT",
                    f"Agent {agent_info} is attacking {self.host_to_attack.ip_address}:{port_to_attack} with service {service_to_attack}",
                )

                action_to_run = None

                if (
                    "CVE-2017-5638" in service_to_attack.CVE
                    and self.host_to_attack.ip_address
                ):
                    action_to_run = ExploitStruts(
                        agent,
                        self.host_to_attack.ip_address,
                        str(port_to_attack),
                    )
                elif port_to_attack == 4444 and self.host_to_attack.ip_address:
                    action_to_run = NCLateralMove(
                        agent,
                        self.host_to_attack.ip_address,
                        str(port_to_attack),
                    )

                if action_to_run is None:
                    continue

                new_events = await low_level_action_orchestrator.run_action(
                    action_to_run
                )

                if len(new_events) > 0:
                    if self.stop_after_success:
                        return new_events
                    else:
                        events += new_events

        return events
