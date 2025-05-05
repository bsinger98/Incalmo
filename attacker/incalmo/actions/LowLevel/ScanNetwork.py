from ..LowLevelAction import LowLevelAction

from app.objects.c_agent import Agent
from app.objects.secondclass.c_fact import Fact
from app.service.knowledge_svc import KnowledgeService
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService

from plugins.deception.app.models.events import Event, HostsDiscovered


class ScanNetwork(LowLevelAction):
    ability_name = "deception-nmapsubnet"

    def __init__(self, agent: Agent, subnet_mask: str):
        facts = {
            "scan.subnet.addr": subnet_mask,
        }
        reset_facts = ["host.subnet.online_ipaddrs"]
        super().__init__(
            agent, facts, ScanNetwork.ability_name, reset_facts=reset_facts
        )

        self.subnet = subnet_mask

    async def get_result(
        self,
        operation: Operation,
        planner: PlanningService,
        knowledge_svc_handle: KnowledgeService,
        raw_result: dict | None = None,
    ) -> list[Event]:
        # Collect all hosts to scan from fact
        collected_ips = []
        online_ips = await knowledge_svc_handle.get_facts(
            criteria=dict(
                trait="host.subnet.online_ipaddrs",
                source=operation.id,
                collected_by=[self.agent.paw],
            )
        )

        for fact in online_ips:
            for ip in fact.value:
                collected_ips.append(ip)

        if len(collected_ips) == 0:
            return []
        else:
            return [HostsDiscovered(self.subnet, collected_ips)]
