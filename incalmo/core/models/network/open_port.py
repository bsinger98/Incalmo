from pydantic import BaseModel


class OpenPort(BaseModel):
    port: int
    service: str
    CVE: list[str] = []
