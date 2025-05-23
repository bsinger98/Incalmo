from pydantic import BaseModel, Field
from typing import List, Dict


class Instruction(BaseModel):
    id: str
    command: str
    executor: str
    payloads: List[str] = Field(default_factory=list)
    uploads: List[Dict[str, str]] = Field(default_factory=list)
    sleep: int = 0
    timeout: int = 60
    deadman: bool = False
    delete_payload: bool = True

    @property
    def display(self) -> dict:
        """Return a clean dictionary representation of the instruction."""
        return self.model_dump(exclude_none=True)

    class Config:
        from_attributes = True
