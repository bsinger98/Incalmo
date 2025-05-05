from ansible.AnsiblePlaybook import AnsiblePlaybook


class AddToSSHConfig(AnsiblePlaybook):
    def __init__(
        self, host: str, host_user: str, follower: str, follower_user: str
    ) -> None:
        self.name = "deployment_instance/setup_server_ssh_keys/add_to_ssh_config.yml"
        self.params = {
            "host": host,
            "host_user": host_user,
            "follower": follower,
            "follower_user": follower_user,
        }
