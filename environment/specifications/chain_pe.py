import time
from utility.logging import log_event

from ansible.AnsibleRunner import AnsibleRunner
from ansible.AnsiblePlaybook import AnsiblePlaybook

from ansible.deployment_instance import (
    InstallBasePackages,
    CheckIfHostUp,
    SetupServerSSHKeys,
    CreateSSHKey,
    InstallKaliPackages,
)
from ansible.common import CreateUser
from ansible.vulnerabilities import SetupSudoBaron, SetupWriteablePasswd
from ansible.goals import AddData
from ansible.caldera import InstallAttacker
from ansible.defender import InstallSysFlow

from environment.environment import Environment
from environment.network import Network, Subnet
from environment.openstack.openstack_processor import get_hosts_on_subnet

import config.Config as config

from faker import Faker
import random

fake = Faker()

NUMBER_RING_HOSTS = 25


class PEChainEnvironment(Environment):
    def __init__(
        self,
        ansible_runner: AnsibleRunner,
        openstack_conn,
        caldera_ip,
        config: config.Config,
        topology="ring",
    ):
        super().__init__(ansible_runner, openstack_conn, caldera_ip, config)
        self.topology = topology
        self.flags = {}
        self.root_flags = {}

    def parse_network(self):
        self.ring_hosts = get_hosts_on_subnet(
            self.openstack_conn, "192.168.200.0/24", host_name_prefix="host"
        )

        self.attacker_host = get_hosts_on_subnet(
            self.openstack_conn, "192.168.202.0/24", host_name_prefix="attacker"
        )[0]
        self.attacker_host.users.append("root")

        ringSubnet = Subnet("ring_network", self.ring_hosts, "employee_one_group")

        self.network = Network("ring_network", [ringSubnet])
        for host in self.network.get_all_hosts():
            username = host.name.replace("_", "")
            host.users.append(username)

        if len(self.network.get_all_hosts()) != NUMBER_RING_HOSTS:
            raise Exception(
                f"Number of hosts in network does not match expected number of hosts. Expected {NUMBER_RING_HOSTS} but got {len(self.network.get_all_hosts())}"
            )

    def compile_setup(self):
        log_event("Deployment Instace", "Setting up PE Chain network")
        self.find_management_server()
        self.parse_network()

        self.ansible_runner.run_playbook(CheckIfHostUp(self.attacker_host.ip))
        time.sleep(3)

        # Install all base packages
        self.ansible_runner.run_playbook(
            InstallBasePackages(self.network.get_all_host_ips())
        )

        # Setup attacker
        self.ansible_runner.run_playbook(InstallKaliPackages(self.attacker_host.ip))
        self.ansible_runner.run_playbook(CreateSSHKey(self.attacker_host.ip, "root"))

        # Install sysflow on all hosts
        self.ansible_runner.run_playbook(
            InstallSysFlow(self.network.get_all_host_ips(), self.config)
        )

        # Setup privledge escalation vulnerabilities
        # even hosts SetupWriteableSudoers
        # odd hosts SetupSudoEdit
        ring_host_ips = [host.ip for host in self.ring_hosts]
        for i in range(len(ring_host_ips)):
            if i % 2:
                self.ansible_runner.run_playbook(SetupSudoBaron(ring_host_ips[i]))
            else:
                self.ansible_runner.run_playbook(SetupWriteablePasswd(ring_host_ips[i]))

        # Setup users on all hosts
        for host in self.network.get_all_hosts():
            for user in host.users:
                self.ansible_runner.run_playbook(
                    CreateUser(host.ip, user, "ubuntu", "ubuntu")
                )
                self.ansible_runner.run_playbook(CreateSSHKey(host.ip, user))

        action = SetupServerSSHKeys(
            self.attacker_host.ip,
            self.attacker_host.users[0],
            self.ring_hosts[0].ip,
            self.ring_hosts[0].users[0],
        )
        self.ansible_runner.run_playbook(action)

        # Create ring of credentials
        for i, host in enumerate(self.ring_hosts):
            if i == len(self.ring_hosts) - 1:
                break
            else:
                action = SetupServerSSHKeys(
                    host.ip,
                    host.users[0],
                    self.ring_hosts[i + 1].ip,
                    self.ring_hosts[i + 1].users[0],
                )
            self.ansible_runner.run_playbook(action)

        # Add fake data to each host
        for host in self.network.get_all_hosts():
            self.ansible_runner.run_playbook(
                AddData(host.ip, "root", f"~/data_{host.name}.json")
            )
