from ansible.AnsiblePlaybook import AnsiblePlaybook


class SetupSudoBypass(AnsiblePlaybook):
    def __init__(self, hosts: str | list[str]) -> None:
        self.name = "vulnerabilities/privledge_escalation/sudobypass/sudobypass.yml"
        self.params = {
            "host": hosts,
        }
