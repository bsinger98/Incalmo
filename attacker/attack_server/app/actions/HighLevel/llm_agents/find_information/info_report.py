from pydantic import BaseModel
from typing import List


class Credential(BaseModel):
    hostname: str
    host_ip: str
    username: str
    port: str


class CriticalData(BaseModel):
    file_paths: list[str]


class FindInformationResult(BaseModel):
    results: List[Credential | CriticalData]
