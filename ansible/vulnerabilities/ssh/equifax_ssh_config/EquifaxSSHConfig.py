from ansible.AnsiblePlaybook import AnsiblePlaybook


class EquifaxSSHConfig(AnsiblePlaybook):
    def __init__(self, host: str, host_user: str) -> None:
        self.name = "vulnerabilities/ssh/equifax_ssh_config/equifax_ssh_config.yml"
        self.params = {
            "host": host,
            "host_user": host_user,
        }
