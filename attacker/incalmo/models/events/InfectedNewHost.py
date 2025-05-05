from plugins.deception.app.models.events import Event
from app.objects.c_agent import Agent
from plugins.deception.app.models.network import SSHCredential


class InfectedNewHost(Event):
    def __init__(
        self,
        source_agent: Agent,
        new_agent: Agent,
        credential_used: SSHCredential | None = None,
    ):
        self.source_agent = source_agent
        self.new_agent = new_agent
        self.credential_used: SSHCredential | None = None
        if credential_used:
            self.credential_used = credential_used

    def __str__(self):
        return f"InfectedNewHost: {self.new_agent.host} - {self.new_agent.paw} - {self.new_agent.username}"
