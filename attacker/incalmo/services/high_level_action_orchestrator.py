from typing import TYPE_CHECKING
from plugins.deception.app.models.events.Event import Event

if TYPE_CHECKING:
    from plugins.deception.app.actions.HighLevelAction import HighLevelAction

from plugins.deception.app.services import (
    EnvironmentStateService,
    AttackGraphService,
    LowLevelActionOrchestrator,
)


class HighLevelActionOrchestrator:
    def __init__(
        self,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        high_level_action_log: list[tuple[str, list[str]]] | None = None,
    ):
        self.environment_state_service = environment_state_service
        self.attack_graph_service = attack_graph_service
        self.low_level_action_orchestrator = low_level_action_orchestrator
        if high_level_action_log is None:
            self.high_level_action_log = []
        else:
            self.high_level_action_log = high_level_action_log

    async def run_action(self, action: "HighLevelAction"):
        events = await action.run(
            self.low_level_action_orchestrator,
            self.environment_state_service,
            self.attack_graph_service,
        )
        await self.environment_state_service.parse_events(events)
        self.high_level_action_log.append(
            (str(action), [str(event) for event in events])
        )

        return events
