from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from incalmo.core.strategies.llm.interfaces.llm_agent_interface import LLMAgentInterface


@dataclass
class HighLevelContext:
    hl_id: str
    ll_id: list[str] = field(default_factory=list)
    llm_interface: Optional["LLMAgentInterface"] = None
