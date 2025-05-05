from ..LowLevelAction import LowLevelAction

from app.objects.c_agent import Agent
from app.objects.secondclass.c_fact import Fact
from app.service.knowledge_svc import KnowledgeService
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService

from plugins.deception.app.models.events import Event, ServicesDiscoveredOnHost


class ScanHost(LowLevelAction):
    ability_name = "deception-nmap"
    host: str

    def __init__(self, agent: Agent, host_ip: str):
        facts = {
            "scan.remote.addr": host_ip,
        }

        reset_facts = [
            "host.remote.ip",
            "host.remote.ports",
            "host.remote.port_services",
        ]
        super().__init__(agent, facts, ScanHost.ability_name, reset_facts=reset_facts)

    async def get_result(
        self,
        operation: Operation,
        planner: PlanningService,
        knowledge_svc_handle: KnowledgeService,
        raw_result: dict | None = None,
    ) -> list[Event]:
        # Get host.remote.ip facts for agent
        scanned_host_facts = await knowledge_svc_handle.get_facts(
            criteria=dict(
                trait="host.remote.ip",
                source=operation.id,
                collected_by=[self.agent.paw],
            )
        )

        results = []

        # For each remote fact, get all open ports and services
        for fact in scanned_host_facts:
            relationships = await knowledge_svc_handle.get_relationships(
                criteria=dict(source=fact)
            )
            service_port_array = None
            for relationship in relationships:
                # if relationship.edge == "has_open_ports":
                #     ports = relationship.target.value
                if relationship.edge == "has_port_services":
                    service_port_array = relationship.target.value

            if service_port_array:
                services = {}
                for service_port in service_port_array:
                    port_num = int(service_port[0])
                    service = service_port[1]
                    services[port_num] = service

                results.append(ServicesDiscoveredOnHost(fact.value, services))

        return results
