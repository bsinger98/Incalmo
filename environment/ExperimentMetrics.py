from pydantic import BaseModel
from datetime import datetime


class FlagInformation(BaseModel):
    flag: str
    host: str
    is_root_flag: bool
    time_captured: datetime


class DefenderInformation(BaseModel):
    telemetry: str
    strategy: str
    capabilities: dict


class ExperimentResults(BaseModel):
    operation_id: str
    # Experiment times
    start_time: datetime
    start_execution_time: datetime
    end_time: datetime

    # Experiment information
    attacker: str
    defender: DefenderInformation
    deployment_instance: str

    # Experiment metrics
    hosts_infected: list[str]
    flags_captured: list[FlagInformation]
