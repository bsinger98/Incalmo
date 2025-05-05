from ansible.AnsiblePlaybook import AnsiblePlaybook


class CreateUser(AnsiblePlaybook):
    def __init__(self, host, user: str, password: str, group: str = "admin") -> None:
        self.name = "common/createUser/createUser.yml"
        self.params = {"host": host, "user": user, "password": password, "group": group}
