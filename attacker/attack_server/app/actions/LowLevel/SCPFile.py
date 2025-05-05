from ..LowLevelAction import LowLevelAction

from app.objects.c_agent import Agent


class SCPFile(LowLevelAction):
    ability_name = "deception-scp-copy"

    def __init__(
        self,
        agent: Agent,
        ssh_ip: str,
        ssh_user: str,
        ssh_port: str,
        src_filepath: str,
        dst_filepath: str,
    ):
        facts = {
            "host.data.ip": ssh_ip,
            "host.data.user": ssh_user,
            "host.data.port": ssh_port,
            "host.data.filepath": src_filepath,
            "host.data.dst-filepath": dst_filepath,
        }
        super().__init__(agent, facts, SCPFile.ability_name)
