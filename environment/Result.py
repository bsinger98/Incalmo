from pydantic import BaseModel
from scenarios.Scenario import Scenario
import enum


class FlagType(enum.Enum):
    USER = ("user",)
    ROOT = ("root",)


class FlagInformation(BaseModel):
    flag: str
    host: str
    type: FlagType
    time_found: float


class DataExfiltrated(BaseModel):
    name: str
    time_exfiltrated: float


class HostInfected(BaseModel):
    name: str
    time_infected: float


class ExperimentResult(BaseModel):
    scenario: Scenario
    experiment_time: float
    execution_time: float
    setup_time: float
    flags_captured: list[FlagInformation]
    data_exfiltrated: list[DataExfiltrated]
    hosts_infected: list[HostInfected | str]
    operation_id: str
    defender_action_counts: dict[str, int]
