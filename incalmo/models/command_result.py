from pydantic import BaseModel


class CommandResult(BaseModel):
    exit_code: str
    id: str
    output: str
    pid: int
    status: str
    stderr: str

    def __str__(self):
        return (
            f"CommandResult: id={self.id}, exit_code={self.exit_code}, "
            f"pid={self.pid}, status={self.status}, output={self.output}, "
            f"stderr={self.stderr}"
        )
