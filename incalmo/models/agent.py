from pydantic import BaseModel, Field
from datetime import datetime


class Agent(BaseModel):
    paw: str
    username: str
    privilege: str
    pid: int
    host_ip_addrs: list[str]
    hostname: str
    last_beacon: datetime = Field(default_factory=datetime.now)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Agent):
            return False
        return self.paw == __value.paw
