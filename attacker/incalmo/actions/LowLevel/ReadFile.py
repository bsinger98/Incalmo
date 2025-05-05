from ..LowLevelAction import LowLevelAction

from app.objects.c_agent import Agent
from app.objects.secondclass.c_fact import Fact
from app.service.knowledge_svc import KnowledgeService
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService

from plugins.deception.app.models.events import Event, FileContentsFound


class ReadFile(LowLevelAction):
    ability_name = "deception-readfile"

    def __init__(self, agent: Agent, file_path: str):
        facts = {"host.file.path": file_path}
        super().__init__(agent, facts, ReadFile.ability_name)
        self.file_path = file_path

    async def get_result(
        self,
        operation: Operation,
        planner: PlanningService,
        knowledge_svc_handle: KnowledgeService,
        raw_result: dict | None = None,
    ) -> list[Event]:
        # See if fact has a new relationship
        file_path_facts = await knowledge_svc_handle.get_facts(
            criteria=dict(
                trait="host.file.path",
                source=operation.id,
                collected_by=[self.agent.paw],
            )
        )

        # Get correct path fact
        flag_path_fact = None
        for fact in file_path_facts:
            if fact.value == self.file_path:
                flag_path_fact = fact
                break

        # Get relationships
        relationships = await knowledge_svc_handle.get_relationships(
            criteria=dict(source=flag_path_fact)
        )

        # Check if it has a contents relationship
        for relationship in relationships:
            if relationship.edge == "has_contents":
                return [
                    FileContentsFound(
                        relationship.source.value, relationship.target.value
                    )
                ]

        return []
