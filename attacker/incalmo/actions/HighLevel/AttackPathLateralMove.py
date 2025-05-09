from incalmo.models.network import AttackPath
from incalmo.actions.high_level_action import HighLevelAction
from incalmo.actions.LowLevel import ExploitStruts, SSHLateralMove, NCLateralMove
from incalmo.models.events import InfectedNewHost, Event
from incalmo.services import (
    LowLevelActionOrchestrator,
    EnvironmentStateService,
    AttackGraphService,
)


class AttackPathLateralMove(HighLevelAction):
    def __init__(self, attack_path: AttackPath, skip_if_already_executed: bool = False):
        self.attack_path = attack_path
        self.skip_if_already_executed = skip_if_already_executed

    async def run(
        self,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
    ) -> list[Event]:
        events = []

        if self.skip_if_already_executed:
            if attack_graph_service.already_executed_attack_path(self.attack_path):
                return []

        if len(self.attack_path.attack_host.agents) == 0:
            return []

        attack_agent = self.attack_path.attack_host.agents[0]
        prior_agents = environment_state_service.get_agents()
        # Mark attack path as executed
        attack_graph_service.executed_attack_path(self.attack_path)

        # Attack based on port
        if (
            self.attack_path.attack_technique.PortToAttack
            and self.attack_path.target_host.ip_address
        ):
            port_to_attack = self.attack_path.attack_technique.PortToAttack
            service_to_attack = self.attack_path.target_host.open_ports[port_to_attack]
            port_to_attack = str(port_to_attack)
            ip_to_attack = self.attack_path.target_host.ip_address

            action_to_run = None

            if "CVE-2017-5638" in service_to_attack.CVE:
                action_to_run = ExploitStruts(
                    attack_agent,
                    ip_to_attack,
                    port_to_attack,
                )

            elif port_to_attack == "4444":
                action_to_run = NCLateralMove(
                    attack_agent,
                    ip_to_attack,
                    port_to_attack,
                )

            if action_to_run:
                log_event("Attacking port: ", f"Executing attack!")
                new_events = await low_level_action_orchestrator.run_action(
                    action_to_run
                )
                log_event("Attacking port: ", f"Finished!")
                events += new_events

        # Attack using credential
        if self.attack_path.attack_technique.CredentialToUse:
            # fmt: off
            log_event("LATERAL MOVE", f"Cred: {self.attack_path.attack_technique.CredentialToUse}")
            # fmt: on
            credential = self.attack_path.attack_technique.CredentialToUse
            new_events = await low_level_action_orchestrator.run_action(
                SSHLateralMove(credential.agent_discovered, credential.hostname)
            )
            for event in new_events:
                if type(event) is InfectedNewHost:
                    event.credential_used = credential
                events.append(event)

        return events
