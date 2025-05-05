from app.objects.c_agent import Agent


class SSHCredential:
    def __init__(
        self,
        hostname: str,
        host_ip: str,
        username: str,
        port: str,
        agent_discovered: Agent,
    ):
        self.hostname = hostname
        self.host_ip = host_ip
        self.username = username
        self.port = port
        self.utilized = False

        self.agent_discovered = agent_discovered

    def __str__(self):
        return f"{self.__class__.__name__}: {self.username}@{self.host_ip}:{self.port}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, SSHCredential):
            return False
        return (
            self.host_ip == __value.host_ip
            and self.username == __value.username
            and self.port == __value.port
        )
