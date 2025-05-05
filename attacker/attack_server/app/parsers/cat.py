from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.utility.base_parser import BaseParser


class Parser(BaseParser):

    def parse(self, blob):

        # Find host.file.path used path
        file_path_fact = None
        for fact in self.used_facts:
            if fact.trait == 'host.file.path':
                file_path_fact = fact
                break
            
        if file_path_fact:
            edge = 'has_contents'
            file_contents_fact = Fact('host.file.contents', blob)

            realationship = Relationship(source=file_path_fact,
                            edge=edge,
                            target=file_contents_fact)

            return [realationship]
        
        return None