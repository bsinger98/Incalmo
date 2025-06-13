from dataclasses import dataclass


@dataclass
class Context:
    hl_id: str
    ll_id: str | None = None
