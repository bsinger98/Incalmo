from ansible.AnsiblePlaybook import AnsiblePlaybook


class SetupWriteableSudoers(AnsiblePlaybook):
    def __init__(self, hosts: str | list[str]) -> None:
        self.name = (
            "vulnerabilities/privledge_escalation/writeableSudoers/writeableSudoers.yml"
        )
        self.params = {
            "host": hosts,
        }
