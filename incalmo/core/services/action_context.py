from dataclasses import dataclass, field


@dataclass
class HighLevelContext:
    hl_id: str
    ll_id: list[str] = field(default_factory=list)
