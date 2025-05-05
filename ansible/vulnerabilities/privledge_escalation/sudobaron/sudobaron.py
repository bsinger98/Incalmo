from ansible.AnsiblePlaybook import AnsiblePlaybook


class SetupSudoBaron(AnsiblePlaybook):
    def __init__(self, hosts: str | list[str]) -> None:
        self.name = "vulnerabilities/privledge_escalation/sudobaron/sudobaron.yml"
        self.params = {
            "host": hosts,
        }
