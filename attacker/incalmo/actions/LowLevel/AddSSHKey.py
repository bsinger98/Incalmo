from ..low_level_action import LowLevelAction

from models.attacker.agent import Agent


class AddSSHKey(LowLevelAction):

    def __init__(self, agent: Agent, public_ssh_key: str):
        self.public_ssh_key = public_ssh_key

        command = f"echo '{public_ssh_key}' >> ~/.ssh/authorized_keys; sed -i 's/\\\\//g' ~/.ssh/authorized_keys"
        
        super().__init__(agent, command)
