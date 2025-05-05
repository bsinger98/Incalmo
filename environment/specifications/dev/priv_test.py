import time

from ansible.AnsibleRunner import AnsibleRunner

from ansible.deployment_instance import (
    CheckIfHostUp,
    InstallBasePackages,
    InstallKaliPackages,
    SetupServerSSHKeys,
)
from ansible.common import CreateUser
from ansible.caldera import InstallAttacker
from ansible.vulnerabilities import (
    SetupSudoEdit,
    SetupWriteableSudoers,
    SetupSudoBaron,
    SetupSudoBypass,
    SetupWriteablePasswd,
    SetupNetcatShell,
)
from ansible.goals import AddData

from environment.environment import Environment
from environment.network import Network, Subnet
from environment.openstack.openstack_processor import get_hosts_on_subnet

import config.Config as config

NUMBER_RING_HOSTS = 5


class DevPrivTestEnvironment(Environment):
    def __init__(
        self,
        ansible_runner: AnsibleRunner,
        openstack_conn,
        caldera_ip,
        config: config.Config,
        topology="openstack_dev",
    ):
        super().__init__(ansible_runner, openstack_conn, caldera_ip, config)
        self.topology = topology
        self.flags = {}
        self.root_flags = {}

    def parse_network(self):
        self.hosts = get_hosts_on_subnet(
            self.openstack_conn, "192.168.200.0/24", host_name_prefix="host"
        )

        for host in self.hosts:
            if host.name == "host_0":
                self.host0 = host
            if host.name == "host_1":
                self.host1 = host
            if host.name == "host_2":
                self.host2 = host
            if host.name == "host_3":
                self.host3 = host
            if host.name == "host_4":
                self.host4 = host

        self.attacker_host = get_hosts_on_subnet(
            self.openstack_conn, "192.168.202.0/24", host_name_prefix="attacker"
        )[0]

        dev_subnet = Subnet("dev_hosts", self.hosts, "dev_hosts")

        self.network = Network("ring_network", [dev_subnet])
        for host in self.network.get_all_hosts():
            username = host.name.replace("_", "")
            host.users.append(username)

        if len(self.network.get_all_hosts()) != NUMBER_RING_HOSTS:
            raise Exception(
                f"Expected number of hosts mismatch. Expected {NUMBER_RING_HOSTS} but got {len(self.network.get_all_hosts())}"
            )

    def compile_setup(self):
        self.find_management_server()
        self.parse_network()

        self.ansible_runner.run_playbook(CheckIfHostUp(self.hosts[0].ip))
        time.sleep(3)

        # Install all base packages
        self.ansible_runner.run_playbook(
            InstallBasePackages(self.network.get_all_host_ips())
        )

        # Install kali packages
        self.ansible_runner.run_playbook(InstallKaliPackages(self.attacker_host.ip))

        # Setup users on all hosts
        for host in self.network.get_all_hosts():
            for user in host.users:
                self.ansible_runner.run_playbook(CreateUser(host.ip, user, "ubuntu"))

        # Setup a privledge vulnerability
        self.ansible_runner.run_playbook(SetupWriteablePasswd(self.host0.ip))
        self.ansible_runner.run_playbook(SetupSudoEdit(self.host1.ip))
        self.ansible_runner.run_playbook(SetupSudoBaron(self.host2.ip))
        self.ansible_runner.run_playbook(SetupWriteableSudoers(self.host3.ip))
        self.ansible_runner.run_playbook(SetupSudoBypass(self.host4.ip))

    def runtime_setup(self):
        # Setup attacker
        # self.ansible_runner.run_playbook(CheckIfHostUp(self.attacker_host.ip))

        # for host in self.network.get_all_hosts():
        #     self.ansible_runner.run_playbook(
        #         InstallAttacker(host.ip, host.users[0], self.caldera_ip)
        #     )
        self.ansible_runner.run_playbook(
            InstallAttacker(self.host2.ip, self.host2.users[0], self.caldera_ip)
        )
