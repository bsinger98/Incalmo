import re

from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.utility.base_parser import BaseParser

pattern = r"^\s*(.*?)\s*->\s*(\S+)"


class Parser(BaseParser):
    def parse(self, blob):
        relationships = []
        for match in re.findall(pattern, blob, re.MULTILINE):
            hostname, host_info = match

            hostname_fact = Fact("remote.ssh.hostname", hostname)
            hostinfo_fact = Fact("remote.ssh.hostinfo", host_info)

            relationships.append(
                Relationship(
                    source=hostname_fact,
                    edge="has",
                    target=hostinfo_fact,
                )
            )

        return relationships
