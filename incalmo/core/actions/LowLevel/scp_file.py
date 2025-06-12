from ..low_level_action import LowLevelAction

from incalmo.core.models.attacker.agent import Agent


class SCPFile(LowLevelAction):
    def __init__(
        self,
        agent: Agent,
        ssh_ip: str,
        ssh_user: str,
        ssh_port: str,
        src_filepath: str,
        dst_filepath: str,
        high_level_action_id: str,
    ):
        self.ssh_ip = ssh_ip
        self.ssh_user = ssh_user
        self.ssh_port = ssh_port
        self.src_filepath = src_filepath
        self.dst_filepath = dst_filepath

        command = (
            f"scp -o StrictHostKeyChecking=no -P {ssh_port} "
            f"{ssh_user}@{ssh_ip}:{src_filepath} {dst_filepath}"
        )
        super().__init__(agent, command, high_level_action_id=high_level_action_id)
