import random
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService
from plugins.deception.app.helpers.logging import (
    get_logger,
    log_event,
)

from plugins.deception.app.strategies.perry_strategy import PerryStrategy

from plugins.deception.app.actions.HighLevel import (
    FindInformationOnAHost,
    AttackPathLateralMove,
    Scan,
    ExfiltrateData,
)
from plugins.deception.app.models.network import (
    AttackPath,
    AttackTechnique,
)
from plugins.deception.app.models.events import HostsDiscovered, InfectedNewHost
from enum import Enum

plugin_logger = get_logger()


class EquifaxAttackerState(Enum):
    InitialAccess = 0
    CredExfiltrate = 1
    Finished = 2


class LogicalPlanner(PerryStrategy):
    def __init__(
        self,
        operation: Operation,
        planning_svc: PlanningService,
        stopping_conditions=(),
    ):
        super().__init__(operation, planning_svc, stopping_conditions)

        self.state = EquifaxAttackerState.InitialAccess

    async def step(self) -> bool:
        if self.state == EquifaxAttackerState.InitialAccess:
            await self.initial_access()
        elif self.state == EquifaxAttackerState.CredExfiltrate:
            await self.cred_exfiltrate()
        elif self.state == EquifaxAttackerState.Finished:
            return True

        return False

    async def initial_access(self):
        self.attacker_host = self.initial_hosts[0]

        if self.external_subnet is None:
            # Use attacker host to scan external network
            events = await self.high_level_action_orchestrator.run_action(
                Scan(
                    self.attacker_host,
                    self.environment_state_service.network.get_non_infected_subnets(),
                )
            )

            for event in events:
                if type(event) is HostsDiscovered:
                    if len(event.host_ips) > 0:
                        self.external_subnet = self.environment_state_service.network.find_subnet_by_ip_mask(
                            event.subnet_ip_mask
                        )
                        break

        if self.external_subnet is None:
            log_event("INITIAL_ACCESS", "Could not find external subnet")
            self.state = EquifaxAttackerState.Finished
            return

        # Randomize order of hosts
        random.shuffle(self.external_subnet.hosts)
        for host in self.external_subnet.hosts:
            if host.infected:
                continue

            # For each host on external network, try to infect
            log_event("INITIAL_ACCESS", f"Trying to infect host: {host}")

            all_events = []
            attack_paths = self.attack_graph_service.get_possible_attack_paths(
                self.attacker_host, host
            )
            for path in attack_paths:
                events = await self.high_level_action_orchestrator.run_action(
                    AttackPathLateralMove(path)
                )
                all_events.extend(events)

            # If any events are of type InfectedNewHost
            for event in all_events:
                if type(event) is InfectedNewHost:
                    # fmt: off
                    log_event("INITIAL_ACCESS", f"Infected host, moving to cred exfiltrate")
                    # fmt: on

                    self.new_initial_access_agent = event.new_agent
                    self.new_initial_access_host = host
                    self.state = EquifaxAttackerState.CredExfiltrate
                    return

        # Couldn't get initial access, end operation
        self.state = EquifaxAttackerState.Finished

    async def cred_exfiltrate(self):
        if (
            self.new_initial_access_agent is None
            or self.new_initial_access_host is None
        ):
            log_event("CRED_EXFILTRATE", "No new initial access agent or host")
            self.state = EquifaxAttackerState.Finished
            return

        # Discover information about host
        events = await self.high_level_action_orchestrator.run_action(
            FindInformationOnAHost(self.new_initial_access_host)
        )

        if len(self.new_initial_access_host.ssh_config) == 0:
            log_event("CRED_EXFILTRATE", "No SSH config found")
            # Try attacking other initial access servers
            self.state = EquifaxAttackerState.InitialAccess
            return

        # Found ssh, infect hosts in ssh config
        random.shuffle(self.new_initial_access_host.ssh_config)
        for credential in self.new_initial_access_host.ssh_config:
            # fmt: off
            log_event("SSH LATERAL MOVE", f"Trying to infect SSH credential: {credential}")
            # fmt: on

            target_host = self.environment_state_service.network.find_host_by_ip(
                credential.host_ip
            )

            if target_host:
                attack_path = AttackPath(
                    attack_host=self.new_initial_access_host,
                    target_host=target_host,
                    attack_technique=AttackTechnique(CredentialToUse=credential),
                )
                events = await self.high_level_action_orchestrator.run_action(
                    AttackPathLateralMove(attack_path)
                )

                # Check if credential was succesful
                infected_host = None
                for event in events:
                    if type(event) is InfectedNewHost:
                        infected_host = (
                            self.environment_state_service.network.find_host_by_agent(
                                event.new_agent
                            )
                        )
                        break

                # If infected new host, find info and exfiltrate
                if infected_host is not None:
                    events = await self.high_level_action_orchestrator.run_action(
                        FindInformationOnAHost(infected_host)
                    )

                    events = await self.high_level_action_orchestrator.run_action(
                        ExfiltrateData(infected_host)
                    )

        # Try attacking other initial access servers
        self.state = EquifaxAttackerState.InitialAccess
        return
