class Results:
    def __init__(
        self,
        message: str | None,
        agent_time: str | None,
        exit_code: str | None,
        id: str | None,
        pid: str | None,
        status: str | None,
        stdout: str | None,
        stderr: str | None,
    ):
        self.message = message
        self.agent_time = agent_time
        self.exit_code = exit_code
        self.id = id
        self.pid = pid
        self.status = status
        self.stdout = stdout
        self.stderr = stderr
