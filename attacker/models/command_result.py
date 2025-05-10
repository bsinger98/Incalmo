from pydantic import BaseModel


class CommandResult(BaseModel):
    exit_code: str
    id: str
    output: str
    pid: int
    status: str
    stderr: str
