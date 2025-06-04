from pydantic import BaseModel
from typing import List
from .host import Host


class ScanResults(BaseModel):
    results: List[Host]
