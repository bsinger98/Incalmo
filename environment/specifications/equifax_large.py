from .equifax_instance import EquifaxInstance
from ansible.AnsibleRunner import AnsibleRunner


class EquifaxLarge(EquifaxInstance):
    def __init__(
        self,
        ansible_runner: AnsibleRunner,
        openstack_conn,
        caldera_ip,
        config,
    ):
        topology = "equifax_large"
        number_of_hosts = 50
        super().__init__(
            ansible_runner,
            openstack_conn,
            caldera_ip,
            config,
            topology,
            number_of_hosts,
        )
