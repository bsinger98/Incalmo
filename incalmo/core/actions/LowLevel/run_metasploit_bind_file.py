from ..low_level_action import LowLevelAction
from incalmo.models.agent import Agent


class RunMetasploitBindFile(LowLevelAction):
    def __init__(self, agent: Agent):

        command = "chmod +x ./bind_metasploit_session && nohup ./bind_metasploit_session > /dev/null 2>&1 &"
        payloads = ["bind_metasploit_session"]

        super().__init__(agent, command, payloads=payloads, command_delay=3)
