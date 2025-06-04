from pydantic import BaseModel
from typing import List
from .open_port import OpenPort


class ScanHost(BaseModel):
    ip: str
    open_ports: List[OpenPort]


class ScanResults(BaseModel):
    results: List[ScanHost]
