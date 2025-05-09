from incalmo.models.events import Event
from incalmo.models.network import SSHCredential
from incalmo.models.attacker.agent import Agent


class CredentialFound(Event):
    def __init__(self, agent: Agent):
        self.agent = agent

    def __str__(self):
        return f"{self.__class__.__name__} on host {self.agent.hostname}"


class SSHCredentialFound(CredentialFound):
    def __init__(
        self,
        agent: Agent,
        hostname: str,
        ssh_username: str,
        ssh_host: str,
        port: str,
    ):
        super().__init__(agent)
        self.credential = SSHCredential(
            hostname, ssh_host, ssh_username, port, self.agent
        )

    def __str__(self):
        return f"{self.__class__.__name__}: on host {self.agent.hostname} with {self.credential}"
