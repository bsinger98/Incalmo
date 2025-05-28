from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from incalmo.core.actions.high_level_action import HighLevelAction

from incalmo.core.services import (
    EnvironmentStateService,
    AttackGraphService,
    LowLevelActionOrchestrator,
)

from incalmo.core.services.logging_service import PerryLogger


class HighLevelActionOrchestrator:
    def __init__(
        self,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        logging_service: PerryLogger,
    ):
        self.environment_state_service = environment_state_service
        self.attack_graph_service = attack_graph_service
        self.low_level_action_orchestrator = low_level_action_orchestrator
        self.logger = logging_service.setup_logger(logger_name="high_level_action")

    async def run_action(self, action: "HighLevelAction"):
        self.logger.info(f"High_level_action: \n{str(action)}")
        events = await action.run(
            self.low_level_action_orchestrator,
            self.environment_state_service,
            self.attack_graph_service,
        )
        self.logger.info(
            "Events generated:\n" + "\n".join(str(event) for event in events)
        )
        await self.environment_state_service.parse_events(events)

        return events
