from ..LowLevelAction import LowLevelAction

from app.objects.c_agent import Agent


class CopyFile(LowLevelAction):
    ability_name: str = "deception-copyfile"

    def __init__(self, agent: Agent, source_path: str, destination_path: str):
        facts = {
            "host.dir.sourcePath": source_path,
            "host.dir.destinationPath": destination_path,
        }
        super().__init__(agent, facts, CopyFile.ability_name)
