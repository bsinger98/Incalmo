from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.utility.base_parser import BaseParser

import os
import time


class Parser(BaseParser):
    def parse(self, blob):
        # Parse the results of the ls command
        lines = blob.split("\n")
        relationships = []

        for line in lines:
            if line == "":
                continue
            elif "data" in line:
                file_hash = line.split()[0]
                filename = line.split()[1]
                filename = os.path.basename(filename)

                # Create a file fact
                file_fact = Fact("results.data.filename", filename)
                hash_fact = Fact("results.data.hash", file_hash)

                file_realationship = Relationship(
                    source=file_fact, edge="has_hash", target=hash_fact
                )

                relationships.append(file_realationship)

                # timestamp_fact = Fact("results.data.timestamp", int(time.time()))
                # time_relationship = Relationship(
                #     source=file_fact, edge="has_timestamp", target=timestamp_fact
                # )
                # relationships.append(time_relationship)

        return relationships
