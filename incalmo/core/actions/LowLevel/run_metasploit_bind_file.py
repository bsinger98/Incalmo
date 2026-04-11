from ..low_level_action import LowLevelAction
from incalmo.models.agent import Agent
from incalmo.core.services.config_service import ConfigService


class RunMetasploitBindFile(LowLevelAction):
    def __init__(self, agent: Agent):

        command = "chmod +x /agents/bind_metasploit_session && /agents/bind_metasploit_session &"
        payloads = ["bind_metasploit_session"]

        super().__init__(agent, command, payloads=payloads, command_delay=3)
