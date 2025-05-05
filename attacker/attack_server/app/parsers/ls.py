from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.utility.base_parser import BaseParser

import os


class Parser(BaseParser):
    def parse(self, blob):
        # Parse the results of the ls command
        dir_path_fact = None
        for fact in self.used_facts:
            if fact.trait == "host.dir.path":
                dir_path_fact = fact
                break

        if dir_path_fact:
            edge = "has_contents"
            directories = []
            files = []
            lines = blob.split("\n")
            search_dir = dir_path_fact.value

            for line in lines:
                if line == "":
                    continue
                elif line.startswith("d"):
                    directory = line.split()[-1]
                    directory = os.path.join(search_dir, directory)
                    directories.append(directory)
                elif line.startswith("-"):
                    file = line.split()[-1]
                    file = os.path.join(search_dir, file)
                    files.append(file)

            relationships = []

            if len(files) > 0:
                files_fact = Fact("host.dir.files", files)
                file_realationship = Relationship(
                    source=dir_path_fact, edge=edge, target=files_fact
                )
                relationships.append(file_realationship)
            if len(directories) > 0:
                dir_fact = Fact("host.dir.dirs", directories)
                dir_realationship = Relationship(
                    source=dir_path_fact, edge=edge, target=dir_fact
                )
                relationships.append(dir_realationship)

            return relationships

        return None
