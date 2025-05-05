from ansible.AnsiblePlaybook import AnsiblePlaybook


class SSHEnablePasswordLogin(AnsiblePlaybook):
    def __init__(self, host: str) -> None:
        self.name = "vulnerabilities/ssh/sshEnablePasswordLogin.yml"
        self.params = {
            "host": host,
        }
