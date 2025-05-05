class Host:
    def __init__(self, name: str, ip: str, users: list[str] | None = None):
        self.name = name
        self.ip = ip
        self.decoy_users = []

        if users is None:
            self.users = []
        else:
            self.users = users

    def add_user(self, user: str, is_decoy: bool = False):
        if is_decoy:
            self.decoy_users.append(user)
        else:
            self.users.append(user)
