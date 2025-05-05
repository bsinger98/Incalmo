from ..LowLevelAction import LowLevelAction
from plugins.deception.app.models.events import Event, FilesFound
from plugins.deception.app.helpers.logging import log_event

from app.objects.c_agent import Agent
from app.service.knowledge_svc import KnowledgeService
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService

import asyncio


class ListFilesInDirectory(LowLevelAction):
    def __init__(self, agent: Agent, dir_path: str):
        self.dir_path = dir_path
        facts = {
            "host.dir.path": dir_path,
        }

        ability_name = "deception-ls"

        super().__init__(agent, facts, ability_name)

    async def get_result(
        self,
        operation: Operation,
        planner: PlanningService,
        knowledge_svc_handle: KnowledgeService,
        raw_result: dict | None = None,
    ) -> list[Event]:
        await asyncio.sleep(2)

        # See if fact has a new relationship
        dir_path_facts = await knowledge_svc_handle.get_facts(
            criteria=dict(
                trait="host.dir.path",
                source=operation.id,
            )
        )

        # Get correct path fact
        dir_path_fact = None
        for fact in dir_path_facts:
            if fact.value == self.dir_path:
                dir_path_fact = fact
                break

        log_event("deception-ls", f"dir_path_fact: {dir_path_fact}")
        # Get all relationships
        relationships = await knowledge_svc_handle.get_relationships(
            criteria=dict(source=dir_path_fact)
        )

        # Get all files
        files = None
        for relationship in relationships:
            log_event("deception-ls", f"relationship: {relationship}")
            if (
                relationship.edge == "has_contents"
                and relationship.target.name == "host.dir.files"
            ):
                files = relationship.target.value
                return [FilesFound(self.agent, files=files)]

        return []
