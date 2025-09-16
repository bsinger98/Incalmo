from incalmo.core.strategies.state_machine.graph_search import (
    GraphSearch,
    GraphSearchType,
)
from config.attacker_config import AttackerConfig


class NetworkDFS(GraphSearch):
    def __init__(
        self,
        config: AttackerConfig,
        logger: str = "incalmo",
        task_id: str = "",
    ):
        super().__init__(config, logger, task_id, GraphSearchType.DFS)
