import time
from utility.logging import log_event

from ansible.AnsibleRunner import AnsibleRunner

from ansible.deployment_instance import (
    InstallBasePackages,
    CheckIfHostUp,
    SetupServerSSHKeys,
    CreateSSHKey,
    InstallKaliPackages,
)
from ansible.common import CreateUser
from ansible.goals import AddData
from ansible.caldera import InstallAttacker
from ansible.defender import InstallSysFlow
from ansible.vulnerabilities import SetupSudoBaron, SetupWriteablePasswd
from ansible.vulnerabilities import SetupNetcatShell, SetupStrutsVulnerability

from environment import Environment
from ..network import Network, Subnet
from ..openstack.openstack_processor import get_hosts_on_subnet

import config.Config as config

from faker import Faker
import random

fake = Faker()

NUMBER_RING_HOSTS = 25


class StarPE(Environment):
    def __init__(
        self,
        ansible_runner: AnsibleRunner,
        openstack_conn,
        caldera_ip,
        config: config.Config,
        topology="star",
    ):
        super().__init__(ansible_runner, openstack_conn, caldera_ip, config)
        self.topology = topology
        self.flags = {}
        self.root_flags = {}

    def parse_network(self):
        self.star_hosts = get_hosts_on_subnet(
            self.openstack_conn, "192.168.200.0/24", host_name_prefix="host"
        )

        # Distribute hosts into 3 categories
        self.webservers = self.star_hosts[: len(self.star_hosts) // 3]

        self.nc_hosts = self.star_hosts[
            len(self.star_hosts) // 3 : 2 * len(self.star_hosts) // 3
        ]

        self.ssh_hosts = self.star_hosts[2 * len(self.star_hosts) // 3 :]

        self.attacker_host = get_hosts_on_subnet(
            self.openstack_conn, "192.168.202.0/24", host_name_prefix="attacker"
        )[0]
        self.attacker_host.users.append("root")

        ringSubnet = Subnet("ring_network", self.star_hosts, "employee_one_group")
        self.network = Network("ring_network", [ringSubnet])

        # Setup tomcat users on all webservers
        for host in self.webservers:
            host.users.append("tomcat")

        # Setup normal users on all hosts
        for host in self.nc_hosts + self.ssh_hosts:
            username = host.name.replace("_", "")
            host.users.append(username)

        if len(self.network.get_all_hosts()) != NUMBER_RING_HOSTS:
            raise Exception(
                f"Number of hosts in network does not match expected number of hosts. Expected {NUMBER_RING_HOSTS} but got {len(self.network.get_all_hosts())}"
            )

    def compile_setup(self):
        log_event("Deployment Instace", "Setting up ICS network")
        self.find_management_server()
        self.parse_network()

        self.ansible_runner.run_playbook(CheckIfHostUp(self.attacker_host.ip))
        time.sleep(3)

        # Install all base packages
        self.ansible_runner.run_playbook(
            InstallBasePackages(self.network.get_all_host_ips())
        )
        self.ansible_runner.run_playbook(InstallKaliPackages(self.attacker_host.ip))

        # Install sysflow on all hosts
        self.ansible_runner.run_playbook(
            InstallSysFlow(self.network.get_all_host_ips(), self.config)
        )

        # Setup users on all hosts
        for host in self.network.get_all_hosts():
            for user in host.users:
                self.ansible_runner.run_playbook(CreateUser(host.ip, user, "ubuntu"))
        for host in self.webservers:
            self.ansible_runner.run_playbook(CreateSSHKey(host.ip, host.users[0]))

        # Setup privilege escalation vulnerabilities on all hosts
        for i in range(0, len(self.star_hosts), 2):
            self.ansible_runner.run_playbook(SetupSudoBaron(self.star_hosts[i].ip))
        for i in range(1, len(self.star_hosts), 2):
            self.ansible_runner.run_playbook(
                SetupWriteablePasswd(self.star_hosts[i].ip)
            )

        # Setup apache struts vulnerabilities
        for host in self.webservers:
            self.ansible_runner.run_playbook(SetupStrutsVulnerability(host.ip))

        # Setup netcat shell
        for host in self.nc_hosts:
            self.ansible_runner.run_playbook(SetupNetcatShell(host.ip, host.users[0]))

        # Attacker host has all credentials
        for i, host in enumerate(self.ssh_hosts):
            action = SetupServerSSHKeys(
                self.attacker_host.ip,
                self.attacker_host.users[0],
                host.ip,
                host.users[0],
            )
            self.ansible_runner.run_playbook(action)

        # Add fake data to each host
        for host in self.star_hosts:
            self.ansible_runner.run_playbook(
                AddData(host.ip, "root", f"~/data_{host.name}.json")
            )
