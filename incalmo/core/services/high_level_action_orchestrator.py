from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from incalmo.core.actions.high_level_action import HighLevelAction

from incalmo.core.services import (
    EnvironmentStateService,
    AttackGraphService,
    LowLevelActionOrchestrator,
)

from incalmo.core.services.logging_service import IncalmoLogger
from incalmo.core.services.action_context import Context
from incalmo.models.logging_schema import serialize
from datetime import datetime
from uuid import uuid4


class HighLevelActionOrchestrator:
    def __init__(
        self,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        logging_service: IncalmoLogger,
    ):
        self.environment_state_service = environment_state_service
        self.attack_graph_service = attack_graph_service
        self.low_level_action_orchestrator = low_level_action_orchestrator
        self.logger = logging_service.action_logger()

    async def run_action(self, action: "HighLevelAction"):
        hl_id = str(uuid4())
        context = Context(hl_id=hl_id)
        events = await action.run(
            self.low_level_action_orchestrator,
            self.environment_state_service,
            self.attack_graph_service,
            context,
        )
        self.logger.info(
            "HighLevelAction started execution",
            type="HighLevelAction",
            timestamp=datetime.now().isoformat(),
            high_level_action_id=context.hl_id,
            action_name=action.__class__.__name__,
            action_params=serialize(action),
            action_results={
                event.__class__.__name__: serialize(event) for event in events
            },
        )
        await self.environment_state_service.parse_events(events)

        return events
