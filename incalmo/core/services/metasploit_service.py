from typing import Any, Optional

from pymetasploit3.msfrpc import MsfRpcClient, ExploitModule, MsfRpcError

from incalmo.core.models.metasploit.metasploit_models import (
    MetasploitExploitResult,
    ExploitModuleInfo,
    ExploitModuleOptions,
    PayloadModuleOptions,
)

_RANK_ORDER = {
    "excellent": 0,
    "great": 1,
    "good": 2,
    "normal": 3,
    "average": 4,
    "low": 5,
    "manual": 6,
}


class MetasploitService:
    def __init__(
        self,
        password: str,
        server: str = "127.0.0.1",
        port: int = 55553,
        ssl: bool = True,
    ):
        self.client = MsfRpcClient(password, server=server, port=port, ssl=ssl)

    def search_exploits(self, cve_id: str) -> list[ExploitModuleInfo]:
        """
        Search for exploit modules matching *cve_id*, sorted best-rank first.
        """
        raw = self.client.modules.search("type:exploit cve:" + cve_id)

        modules = [
            ExploitModuleInfo(
                fullname=entry.get("fullname"),
                name=entry.get("name"),
                rank=entry.get("rank"),
                disclosure_date=entry.get("disclosuredate"),
            )
            for entry in raw
        ]

        modules.sort(key=lambda m: _RANK_ORDER.get(m.rank.lower(), len(_RANK_ORDER)))
        return modules

    def get_exploit_module_options(self, module_fullname: str) -> ExploitModuleOptions:
        """
        Load a module and return a snapshot of its option state.
        """
        module = self.client.modules.use("exploit", module_fullname)

        payloads: list[str] = module.targetpayloads() or []

        return ExploitModuleOptions(
            fullname=module_fullname,
            all_options=module.options or [],
            required_options=module.required or [],
            missing_required=module.missing_required or [],
            current_values=module.runoptions or {},
            available_payloads=payloads,
            targets=module.targets or {},
        )

    def get_payload_options(self, payload_name: str) -> PayloadModuleOptions:
        """
        Load a payload and return its options dict.
        """
        payload = self.client.modules.use("payload", payload_name)
        return PayloadModuleOptions(
            fullname=payload_name,
            all_options=payload.options or [],
            required_options=payload.required or [],
            missing_required=payload.missing_required or [],
            current_values=payload.runoptions or {},
        )

    def run_exploit(
        self,
        cve_id: str,
        exploit_module_fullname: str,
        exploit_options: dict[str, Any],
        payload_module_fullname: str,
        payload_options: dict[str, Any],
    ) -> MetasploitExploitResult:
        """
        Configure and fire a Metasploit exploit.
        """
        # Build exploit
        exploit = self.client.modules.use("exploit", exploit_module_fullname)

        for key, value in exploit_options.items():
            exploit[key] = value

        # Build payload
        payload = self.client.modules.use("payload", payload_module_fullname)

        for key, value in payload_options.items():
            payload[key] = value

        cid = self.client.consoles.console().cid
        console_output = self.client.consoles.console(cid).run_module_with_output(
            exploit, payload=payload
        )
        return MetasploitExploitResult(
            cve_id=cve_id,
            console_cid=cid,
            console_output=console_output,
        )
