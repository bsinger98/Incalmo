from ansible.AnsiblePlaybook import AnsiblePlaybook


class InstallAttacker(AnsiblePlaybook):
    def __init__(self, host: str, user: str, caldera_ip: str) -> None:
        self.name = "caldera/install_attacker.yml"
        self.params = {
            "host": host,
            "user": user,
            "caldera_ip": caldera_ip,
        }
