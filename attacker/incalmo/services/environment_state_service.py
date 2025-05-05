from app.objects.c_agent import Agent
from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.service.knowledge_svc import KnowledgeService
from app.objects.c_operation import Operation

from plugins.deception.app.models.events import (
    HostsDiscovered,
    ServicesDiscoveredOnHost,
    CredentialFound,
    SSHCredentialFound,
    InfectedNewHost,
    CriticalDataFound,
    RootAccessOnHost,
    VulnerableServiceFound,
    ScanReportEvent,
)
from plugins.deception.app.models.network import Host, Subnet

from plugins.deception.app.helpers.agent_helpers import get_trusted_agents

from plugins.deception.app.helpers.logging import log_event

import ipaddress
import time

from plugins.deception.app.services.environment_initializer import (
    EnvironmentInitializer,
)
from plugins.deception.app.data.attacker_config import AttackerConfig
from plugins.deception.app.actions.HighLevel.llm_agents.scan.scan_report import (
    ScanResults,
)
from plugins.deception.app.models.network.open_port import OpenPort


class EnvironmentStateService:
    def __init__(
        self,
        calderaKnowledge_svc: KnowledgeService,
        operation: Operation,
        config: AttackerConfig,
    ):
        self.calderaKnowledge_svc = calderaKnowledge_svc
        self.operation = operation
        self.environment_type = config.environment
        self.c2c_server = config.c2c_server

        # Load initial environment state
        environment_initializer = EnvironmentInitializer(config)
        self.network = environment_initializer.get_initial_environment_state()
        self.initial_hosts = []

    def __str__(self):
        env_status = f"EnvironmentStateService: \n"
        for subnet in self.network.subnets:
            env_status += f"Subnet: {subnet}\n"
            for host in subnet.hosts:
                env_status += f"- Host: {host}\n"

        return env_status

    def initial_assumptions(self):
        return

    def get_agents(self) -> list[Agent]:
        return get_trusted_agents(self.operation)

    def get_hosts_with_agents(self) -> list[Host]:
        hosts = []
        for host in self.network.get_all_hosts():
            if len(host.agents) > 0:
                hosts.append(host)
        return hosts

    def get_hosts_without_agents(self) -> list[Host]:
        hosts = []
        for host in self.network.get_all_hosts():
            if len(host.agents) == 0:
                hosts.append(host)
        return hosts

    async def parse_events(self, events):
        if events is None:
            return

        for event in events:
            if type(event) is HostsDiscovered:
                self.handle_HostsDiscovered(event)

            if type(event) is ServicesDiscoveredOnHost:
                self.handle_ServicesDiscoveredOnHost(event)

            if issubclass(type(event), CredentialFound):
                self.handle_CrendentialFound(event)

            if type(event) is InfectedNewHost:
                await self.handle_InfectedNewHost(event)

            if type(event) is RootAccessOnHost:
                self.handle_rootAccess(event)

            if type(event) is CriticalDataFound:
                self.handle_CriticalDataFound(event)

            if type(event) is VulnerableServiceFound:
                self.handle_VulnerableServiceFound(event)

            if type(event) is ScanReportEvent:
                self.update_network_from_report(event.scan_results)
        return

    def handle_HostsDiscovered(self, event: HostsDiscovered):
        # Find correct subnet
        subnet_to_add = None
        for subnet in self.network.subnets:
            if subnet.ip_mask == event.subnet_ip_mask:
                subnet_to_add = subnet
                break

        if subnet_to_add:
            for host_ip in event.host_ips:
                # Add host to subnet if not already there
                cur_host_ips = [host.ip_address for host in subnet_to_add.hosts]
                if host_ip not in cur_host_ips:
                    subnet_to_add.hosts.append(Host(ip_address=host_ip))

    def handle_ServicesDiscoveredOnHost(self, event: ServicesDiscoveredOnHost):
        # Find host
        host = None
        for subnet in self.network.subnets:
            for _host in subnet.hosts:
                if _host.ip_address == event.host_ip:
                    host = _host
                    break

        if host is None:
            host = Host(ip_address=event.host_ip)
            self.network.add_host(host)

        for port, service in event.services.items():
            host.open_ports[port] = OpenPort(port, service, [])

    def handle_VulnerableServiceFound(self, event: VulnerableServiceFound):
        host = self.network.find_host_by_ip(event.host)
        if host is None:
            host = Host(ip_address=event.host)
            self.network.add_host(host)

        if event.port not in host.open_ports:
            host.open_ports[event.port] = OpenPort(
                event.port, event.service, [event.cve]
            )
        else:
            if event.cve not in host.open_ports[event.port].CVE:
                host.open_ports[event.port].CVE.append(event.cve)

    def handle_CrendentialFound(self, event):
        if type(event) is SSHCredentialFound:
            host = self.network.find_host_by_agent(event.agent)
            if host:
                host.ssh_config.append(event.credential)

            # If target host does not exist, add it
            if self.network.find_host_by_ip(event.credential.host_ip) is None:
                self.network.add_host(Host(ip_address=event.credential.host_ip))

    async def handle_InfectedNewHost(self, event: InfectedNewHost):
        # Add agent to network
        self.add_infected_host(event.new_agent)
        await self.log_infected_host_to_caldera(event)

        if event.credential_used:
            event.credential_used.utilized = True

    def handle_rootAccess(self, event: RootAccessOnHost):
        self.add_infected_host(event.root_agent)

    def handle_CriticalDataFound(self, event: CriticalDataFound):
        user = event.agent.username
        host = event.host

        for file in event.files:
            if user not in host.critical_data_files:
                host.critical_data_files[user] = []

            if file not in host.critical_data_files[user]:
                host.critical_data_files[user].append(file)

    def update_host_agents(self, trusted_agents: list[Agent]):
        # Reset all hosts agents
        all_hosts = self.network.get_all_hosts()
        for host in all_hosts:
            host.agents = []

        # Repopulate host agents
        for agent in trusted_agents:
            self.add_infected_host(agent)

    def add_infected_host(self, new_agent: Agent):
        # Add agent to network
        host = self.network.find_host_by_ip(new_agent.host_ip_addrs[0])

        if host:
            host.hostname = new_agent.host
            host.add_agent(new_agent)
        else:
            log_event(
                "ADDING HOST",
                f"Adding host {new_agent.host_ip_addrs[0]} to network",
            )

            new_host = Host(
                ip_address=new_agent.host_ip_addrs[0],
                hostname=new_agent.host,
                agents=[new_agent],
            )

            # Does subnet exist?
            ip_address = new_agent.host_ip_addrs[0]
            address = ipaddress.ip_address(ip_address)
            subnet_mask = ipaddress.ip_network(f"{address}/24", strict=False)

            subnet = self.network.find_subnet_by_ip_mask(str(subnet_mask))
            if subnet is None:
                subnet = Subnet(
                    ip_mask=str(subnet_mask), attacker_subnet=False, hosts=[new_host]
                )
                self.network.add_subnet(subnet)
            else:
                subnet.hosts.append(new_host)

    async def log_infected_host_to_caldera(self, event: InfectedNewHost):
        host_fact = Fact(trait="results.host.name", value=event.new_agent.host)
        time_fact = Fact(trait="results.host.timestamp", value=time.time())
        result_relationship = Relationship(
            source=host_fact,
            edge="has_timestamp",
            target=time_fact,
            origin=self.operation.id,
        )
        await self.calderaKnowledge_svc.add_relationship(result_relationship)

    def update_network_from_report(self, report: ScanResults):
        for ip_scan_result in report.results:
            host = self.network.find_host_by_ip(ip_scan_result.ip)

            if not host:
                # Add host to network
                host = Host(ip_address=ip_scan_result.ip)
                self.network.add_host(host)

            # Set hosts open ports
            for port in ip_scan_result.open_ports:
                if port.port not in host.open_ports:
                    host.open_ports[port.port] = OpenPort(
                        port.port, port.service, port.CVE
                    )
                else:
                    host.open_ports[port.port].service = port.service
                    host.open_ports[port.port].CVE.extend(port.CVE)

        return

    def set_initial_hosts(self, initial_hosts: list[Host]):
        self.initial_hosts = initial_hosts
