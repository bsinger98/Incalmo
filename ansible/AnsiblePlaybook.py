class AnsiblePlaybook(object):
    def __init__(self, name, host) -> None:
        self.name = name
        self.params = {"host": host}
