from .equifax_instance import EquifaxInstance
from ansible.AnsibleRunner import AnsibleRunner


class EquifaxSmall(EquifaxInstance):
    def __init__(
        self,
        ansible_runner: AnsibleRunner,
        openstack_conn,
        caldera_ip,
        config,
    ):
        topology = "equifax_small"
        number_of_hosts = 14
        super().__init__(
            ansible_runner,
            openstack_conn,
            caldera_ip,
            config,
            topology,
            number_of_hosts,
        )
