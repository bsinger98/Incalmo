from incalmo.models.events import Event
from plugins.deception.app.actions.HighLevel.llm_agents.scan.scan_report import (
    ScanResults,
)


class ScanReportEvent(Event):
    def __init__(self, scan_results: ScanResults):
        self.scan_results = scan_results

    def __str__(self):
        return f"ScanReportEvent: \n {self.scan_results}"
