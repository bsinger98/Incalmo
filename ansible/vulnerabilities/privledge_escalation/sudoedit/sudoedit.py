from ansible.AnsiblePlaybook import AnsiblePlaybook


class SetupSudoEdit(AnsiblePlaybook):
    def __init__(self, hosts: str | list[str]) -> None:
        self.name = "vulnerabilities/privledge_escalation/sudoedit/sudoedit.yml"
        self.params = {
            "host": hosts,
        }
