from ..low_level_action import LowLevelAction
from incalmo.models.agent import Agent
from incalmo.models.command_result import CommandResult

from incalmo.core.models.events import Event, VulnerableServiceFound
import re
import json


class NucleiScan(LowLevelAction):
    def __init__(
        self,
        agent: Agent,
        host: str,
        port: int,
        service: str,
    ):
        self.host = host
        self.port = port
        self.service = service

        command = f"nuclei -u {host}:{port} -timeout 5 -severity critical -j -silent"
        super().__init__(agent, command)

    async def get_result(
        self,
        result: CommandResult,
    ) -> list[Event]:
        if result.output is None:
            return []

        events = []
        cves_found = set()

        # Parse each line as JSON and extract CVE info
        for line in result.output.split("\n"):
            if "GOOGLE_API_KEY" in line or "GOOGLE_API_CX" in line:
                continue
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                # Look for CVE in template field or other fields
                for field in ["template", "template-id"]:
                    if field in data:
                        # Extract CVE pattern (CVE-YYYY-XXXXX)
                        cve_match = re.search(r"(CVE-\d{4}-\d{4,})", data[field])
                        if cve_match:
                            cve = cve_match.group(1)
                            if cve not in cves_found:
                                cves_found.add(cve)
                                events.append(
                                    VulnerableServiceFound(
                                        port=self.port,
                                        host=self.host,
                                        service=self.service,
                                        cve=cve,
                                    )
                                )
            except json.JSONDecodeError:
                continue

        return events
