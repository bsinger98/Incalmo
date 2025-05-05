from ansible.AnsiblePlaybook import AnsiblePlaybook


class SetupWriteablePasswd(AnsiblePlaybook):
    def __init__(self, hosts: str | list[str]) -> None:
        self.name = (
            "vulnerabilities/privledge_escalation/writeablePasswd/writeablePasswd.yml"
        )
        self.params = {
            "host": hosts,
        }
