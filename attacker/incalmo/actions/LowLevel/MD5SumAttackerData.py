from ..LowLevelAction import LowLevelAction

from app.objects.c_agent import Agent
from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.service.knowledge_svc import KnowledgeService
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService

from plugins.deception.app.models.events import Event, ExfiltratedData
from plugins.deception.app.helpers.logging import log_event

import time


class MD5SumAttackerData(LowLevelAction):
    ability_name = "deception-exfil-results"

    def __init__(self, agent: Agent):
        facts = {}
        super().__init__(agent, facts, MD5SumAttackerData.ability_name)

    async def get_result(
        self,
        operation: Operation,
        planner: PlanningService,
        knowledge_svc_handle: KnowledgeService,
        raw_result: dict | None = None,
    ) -> list[Event]:
        file_facts: list[Fact] = await knowledge_svc_handle.get_facts(
            criteria=dict(trait="results.data.filename", source=operation.id),
        )

        timestamp_relationships: list[Relationship] = (
            await knowledge_svc_handle.get_relationships(
                criteria=dict(edge="has_timestamp", origin=operation.id)
            )
        )
        file_facts_with_timestamp = []
        for timestamp_relationship in timestamp_relationships:
            file_facts_with_timestamp.append(timestamp_relationship.source.value)

        events = []
        for file_fact in file_facts:
            if file_fact.value in file_facts_with_timestamp:
                continue

            if "json" not in str(file_fact.value):
                continue

            # fmt: off
            log_event("MD5SumAttackerData", f"Exfiltrated file: {file_fact.value} at {time.time()}")
            # fmt: on

            exfiltrated_data = ExfiltratedData(file=file_fact.value)
            events.append(exfiltrated_data)

            timestamp_fact = Fact(
                trait="results.data.timestamp", value=int(time.time())
            )
            timestamp_relationship = Relationship(
                source=file_fact,
                edge="has_timestamp",
                target=timestamp_fact,
                origin=operation.id,
            )
            await knowledge_svc_handle.add_relationship(timestamp_relationship)

        return events
