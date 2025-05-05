from ansible.AnsiblePlaybook import AnsiblePlaybook


class CheckIfHostUp(AnsiblePlaybook):
    def __init__(self, host) -> None:
        self.name = "deployment_instance/check_if_host_up/check_if_host_up.yml"
        self.params = {"host": host}
