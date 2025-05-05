import time
from utility.logging import log_event

from ansible.AnsibleRunner import AnsibleRunner

from ansible.deployment_instance import (
    InstallBasePackages,
    InstallKaliPackages,
    CheckIfHostUp,
    SetupServerSSHKeys,
    CreateSSHKey,
)
from ansible.common import CreateUser
from ansible.vulnerabilities import SetupStrutsVulnerability
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


class EquifaxInstance(Environment):
    def __init__(
        self,
        ansible_runner: AnsibleRunner,
        openstack_conn,
        caldera_ip,
        config: config.Config,
        topology="equifax_small",
        number_of_hosts=12,
    ):
        super().__init__(ansible_runner, openstack_conn, caldera_ip, config)
        self.topology = topology
        self.flags = {}
        self.root_flags = {}
        self.number_of_hosts = number_of_hosts

    def parse_network(self):
        self.webservers = get_hosts_on_subnet(
            self.openstack_conn, "192.168.200.0/24", host_name_prefix="webserver"
        )
        for host in self.webservers:
            host.users.append("tomcat")

        self.attacker_host = get_hosts_on_subnet(
            self.openstack_conn, "192.168.202.0/24", host_name_prefix="attacker"
        )[0]

        self.employee_hosts = get_hosts_on_subnet(
            self.openstack_conn, "192.168.201.0/24", host_name_prefix="employee"
        )
        for host in self.employee_hosts:
            username = host.name.replace("_", "")
            host.users.append(username)

        self.database_hosts = get_hosts_on_subnet(
            self.openstack_conn, "192.168.201.0/24", host_name_prefix="database"
        )
        for host in self.database_hosts:
            username = host.name.replace("_", "")
            host.users.append(username)

        webserverSubnet = Subnet("webserver_network", self.webservers, "webserver")
        corportateSubnet = Subnet(
            "critical_company_network",
            self.employee_hosts + self.database_hosts,
            "critical_company",
        )

        self.network = Network("equifax_network", [webserverSubnet, corportateSubnet])

        if len(self.network.get_all_hosts()) != self.number_of_hosts:
            raise Exception(
                f"Number of hosts in network does not match expected number of hosts. Expected {self.number_of_hosts} but got {len(self.network.get_all_hosts())}"
            )

    def compile_setup(self):
        log_event("Deployment Instace", "Setting up Equifax Instance")
        self.find_management_server()
        self.parse_network()

        self.ansible_runner.run_playbook(CheckIfHostUp(self.webservers[0].ip))
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

        # Setup apache struts and vulnerability
        webserver_ips = [host.ip for host in self.webservers]
        self.ansible_runner.run_playbook(SetupStrutsVulnerability(webserver_ips))

        # Setup users on corporte hosts
        for host in self.employee_hosts + self.database_hosts:
            for user in host.users:
                self.ansible_runner.run_playbook(CreateUser(host.ip, user, "ubuntu"))
        for host in self.webservers:
            self.ansible_runner.run_playbook(CreateSSHKey(host.ip, host.users[0]))

        # Choose a random webserver to setup SSH keys to all databases and employees
        webserver_with_creds = random.choice(self.webservers)
        for employee in self.employee_hosts:
            self.ansible_runner.run_playbook(
                SetupServerSSHKeys(
                    webserver_with_creds.ip, "tomcat", employee.ip, employee.users[0]
                )
            )
        for database in self.database_hosts:
            self.ansible_runner.run_playbook(
                SetupServerSSHKeys(
                    webserver_with_creds.ip, "tomcat", database.ip, database.users[0]
                )
            )

        # Add data to database hosts
        i = 0
        for database in self.database_hosts:
            self.ansible_runner.run_playbook(
                AddData(database.ip, database.users[0], f"~/data_{database.name}.json")
            )
