from ..LowLevelAction import LowLevelAction

from app.objects.c_agent import Agent


class AddSSHKey(LowLevelAction):
    ability_name = "deception-add-ssh-key"

    def __init__(self, agent: Agent, public_ssh_key: str):
        facts = {"host.data.key": public_ssh_key}
        super().__init__(agent, facts, AddSSHKey.ability_name)
