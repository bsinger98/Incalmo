from ansible.AnsiblePlaybook import AnsiblePlaybook


class InstallKaliPackages(AnsiblePlaybook):
    def __init__(self, hosts: str | list[str]) -> None:
        self.name = "deployment_instance/install_base_packages/kali_packages.yml"
        self.params = {"host": hosts}
