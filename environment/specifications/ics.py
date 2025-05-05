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
from ansible.vulnerabilities import SetupNetcatShell
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

NUMBER_ICS_HOSTS = 47


class ICSEnvironment(Environment):
    def __init__(
        self,
        ansible_runner: AnsibleRunner,
        openstack_conn,
        caldera_ip,
        config: config.Config,
        topology="ics_inspired",
    ):
        super().__init__(ansible_runner, openstack_conn, caldera_ip, config)
        self.topology = topology
        self.flags = {}
        self.root_flags = {}

    def parse_network(self):
        self.employee_one_hosts = get_hosts_on_subnet(
            self.openstack_conn, "192.168.200.0/24", host_name_prefix="employee_A"
        )

        self.manage_one_host = get_hosts_on_subnet(
            self.openstack_conn, "192.168.200.0/24", host_name_prefix="manage"
        )

        self.all_employee_one_hosts = self.employee_one_hosts + self.manage_one_host

        self.manage_two_host = get_hosts_on_subnet(
            self.openstack_conn, "192.168.201.0/24", host_name_prefix="manage"
        )

        self.employee_two_hosts = get_hosts_on_subnet(
            self.openstack_conn, "192.168.201.0/24", host_name_prefix="employee_B"
        )
        self.all_employee_two_hosts = self.employee_two_hosts + self.manage_two_host

        self.manage_hosts = self.manage_one_host + self.manage_two_host

        self.attacker_host = get_hosts_on_subnet(
            self.openstack_conn, "192.168.202.0/24", host_name_prefix="attacker"
        )[0]

        self.ot_sensors = get_hosts_on_subnet(
            self.openstack_conn, "192.168.203.0/24", host_name_prefix="sensor"
        )

        self.ot_hosts = get_hosts_on_subnet(
            self.openstack_conn, "192.168.203.0/24", host_name_prefix="control_host"
        )

        employeeOneSubnet = Subnet(
            "employee_one_network", self.all_employee_one_hosts, "employee_one_group"
        )
        employeeTwoSubnet = Subnet(
            "employee_two_network", self.all_employee_two_hosts, "employee_two_group"
        )
        otSubnet = Subnet("OT_network", self.ot_sensors + self.ot_hosts, "ot_group")

        self.network = Network(
            "ics_inspired", [employeeOneSubnet, employeeTwoSubnet, otSubnet]
        )
        for host in self.network.get_all_hosts():
            username = host.name.replace("_", "")
            host.users.append(username)

        if len(self.network.get_all_hosts()) != NUMBER_ICS_HOSTS:
            raise Exception(
                f"Number of hosts in network does not match expected number of hosts. Expected {NUMBER_ICS_HOSTS} but got {len(self.network.get_all_hosts())}"
            )

    def compile_setup(self):
        log_event("Deployment Instance", "Setting up ICS network")

        self.ansible_runner.run_playbook(CheckIfHostUp(self.employee_one_hosts[0].ip))
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

        # Random employee on subnet one
        for manage_host in self.manage_hosts:
            # Setup netcat shell on vulnerable employee
            self.ansible_runner.run_playbook(
                SetupNetcatShell(manage_host.ip, manage_host.users[0])
            )

            # Each employee has SSH keys to all ot sensors
            for sensor in self.ot_sensors:
                self.ansible_runner.run_playbook(
                    SetupServerSSHKeys(
                        manage_host.ip,
                        manage_host.users[0],
                        sensor.ip,
                        sensor.users[0],
                    )
                )

        # Randomly choose 5 OT sensors to have ssh keys to ot hosts
        critical_sensors = random.sample(self.ot_sensors, 5)
        for i, ot_host in enumerate(self.ot_hosts):
            sensor = critical_sensors[i]
            self.ansible_runner.run_playbook(
                SetupServerSSHKeys(
                    sensor.ip,
                    sensor.users[0],
                    ot_host.ip,
                    ot_host.users[0],
                )
            )

    def runtime_setup(self):
        # Randomly choose 1 employee to have attacker
        employee_hosts = self.employee_one_hosts + self.employee_two_hosts
        employee_host = random.choice(employee_hosts)

        # Setup attacker
        self.ansible_runner.run_playbook(
            InstallAttacker(employee_host.ip, employee_host.users[0], self.caldera_ip)
        )
