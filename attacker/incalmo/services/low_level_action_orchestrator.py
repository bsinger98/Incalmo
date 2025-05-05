from app.service.knowledge_svc import KnowledgeService
from app.objects.c_operation import Operation
from app.service.planning_svc import PlanningService
from app.objects.c_agent import Agent
from app.objects.secondclass.c_fact import Fact

from plugins.deception.app.actions.LowLevelAction import LowLevelAction
from plugins.deception.app.models.events.Event import Event

from plugins.deception.app.helpers.ability_helpers import run_ability
from plugins.deception.app.helpers.agent_helpers import get_trusted_agents
from plugins.deception.app.services.environment_state_service import (
    EnvironmentStateService,
)
from plugins.deception.app.models.events import InfectedNewHost, RootAccessOnHost


class LowLevelActionOrchestrator:
    def __init__(
        self,
        operation: Operation,
        planner: PlanningService,
        knowledge_svc_handle: KnowledgeService,
        environment_state_service: EnvironmentStateService,
        low_level_action_log: list[tuple[str, list[str]]] | None = None,
    ):
        self.operation = operation
        self.planner = planner
        self.knowledge_svc_handle = knowledge_svc_handle
        self.environment_state_service = environment_state_service
        if low_level_action_log is None:
            self.low_level_action_log = []
        else:
            self.low_level_action_log = low_level_action_log

    async def run_action(self, low_level_action: LowLevelAction):
        # Reset any reset facts
        for fact_trait in low_level_action.reset_facts:
            await self.remove_fact(fact_trait, low_level_action.agent)

        # Add action facts
        action_facts = low_level_action.facts
        for fact_trait, fact_value in action_facts.items():
            await self.add_fact(fact_trait, fact_value, low_level_action.agent)

        prior_agents = get_trusted_agents(self.operation)
        # Run the action
        result = await run_ability(
            self.planner,
            self.operation,
            low_level_action.agent,
            low_level_action.ability_name,
        )

        # Get the results
        events = await low_level_action.get_result(
            self.operation, self.planner, self.knowledge_svc_handle, result
        )

        # Check for new agents events
        post_agents = get_trusted_agents(self.operation)
        orchestrator_events = self.check_new_agents(
            low_level_action.agent, prior_agents, post_agents
        )
        events.extend(orchestrator_events)

        self.low_level_action_log.append(
            (str(low_level_action), [str(event) for event in events])
        )
        return events

    async def add_fact(
        self,
        fact_trait: str,
        fact_value: str,
        agent: Agent,
    ):
        await self.remove_fact(fact_trait, agent)

        scan_addr_fact = Fact(
            trait=fact_trait,
            value=fact_value,
            source=self.operation.id,
            collected_by=[agent.paw],
        )

        await self.knowledge_svc_handle.add_fact(fact=scan_addr_fact)

    async def remove_fact(self, fact_trait: str, agent: Agent):
        facts = await self.knowledge_svc_handle.get_facts(
            criteria=dict(
                trait="host.remote.ip",
                source=self.operation.id,
                collected_by=[agent.paw],
            )
        )
        # Delete relationships
        for fact in facts:
            await self.knowledge_svc_handle.delete_relationship(
                criteria=dict(source=fact)
            )
        # Delete all facts
        await self.knowledge_svc_handle.delete_fact(
            criteria=dict(
                trait=fact_trait,
                source=self.operation.id,
            )
        )

    def get_trusted_agents(self):
        return get_trusted_agents(self.operation)

    def check_new_agents(
        self, ability_agent: Agent, prior_agents: list[Agent], post_agents: list[Agent]
    ):
        new_agent = None
        # Find the agent that was added to the operation
        for post_agent in post_agents:
            # If the agent paw was not in the prior agents, then it was added
            if post_agent.paw not in [prior_agent.paw for prior_agent in prior_agents]:
                new_agent = post_agent
                break

        if new_agent:
            # If new agent on same host as ability agent, privledge escalation was successful
            if new_agent.host == ability_agent.host:
                if new_agent.username == "root":
                    return [RootAccessOnHost(new_agent)]
            if new_agent.host != ability_agent.host:
                return [InfectedNewHost(ability_agent, new_agent)]

        return []
