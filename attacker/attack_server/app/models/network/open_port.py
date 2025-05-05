from dataclasses import dataclass


@dataclass
class OpenPort:
    port: int
    service: str
    CVE: list[str]
