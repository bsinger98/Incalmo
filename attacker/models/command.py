from pydantic import BaseModel
from models.instruction import Instruction
from enum import Enum
from models.command_result import CommandResult


class CommandStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Command(BaseModel):
    id: str
    instructions: Instruction
    status: CommandStatus
    result: CommandResult | None = None
