from pydantic import BaseModel
from typing import Optional

from attacker.config.attacker_config import AbstractionLevel
from attacker.config.attacker_config import LLM


class DefenderInformation(BaseModel):
    name: str
    telemetry: str
    strategy: str
    capabilities: dict[str, int]


class AttackerInformation(BaseModel):
    name: str
    strategy: str
    abstraction: Optional[AbstractionLevel] = AbstractionLevel.HIGH_LEVEL
    llm: Optional[LLM] = None


class Scenario(BaseModel):
    attacker: AttackerInformation
    defender: DefenderInformation
    environment: str

    def __str__(self):
        return f"{self.attacker.name}-{self.defender.name}-{self.environment}"


class Experiment(BaseModel):
    scenario: Scenario
    trials: int
    timeout: int = 75
