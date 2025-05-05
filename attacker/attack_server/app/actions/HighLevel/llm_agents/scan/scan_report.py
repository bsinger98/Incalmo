from pydantic import BaseModel
from typing import List


class OpenPort(BaseModel):
    port: int
    service: str
    CVE: list[str] = []


class Host(BaseModel):
    ip: str
    open_ports: List[OpenPort]


class ScanResults(BaseModel):
    results: List[Host]
