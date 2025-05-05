from ansible.AnsiblePlaybook import AnsiblePlaybook


class ResetSSHConfig(AnsiblePlaybook):
    def __init__(self, host: str, host_user: str) -> None:
        self.name = "deployment_instance/setup_server_ssh_keys/reset_ssh_config.yml"
        self.params = {
            "host": host,
            "host_user": host_user,
        }
