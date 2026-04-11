import json
from typing import Any, Optional

from pymetasploit3.msfrpc import MsfRpcClient

from incalmo.core.models.metasploit.metasploit_models import (
    AutorouteResult,
    ExploitModuleInfo,
    ExploitModuleOptions,
    MetasploitModuleResult,
    MetasploitExploitResult,
    MetasploitSessionInfo,
    PayloadModuleOptions,
    RouteTableResult,
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

    def list_sessions(self) -> list[MetasploitSessionInfo]:
        sessions = self.client.sessions.list or {}
        output: list[MetasploitSessionInfo] = []

        for session_id, details in sessions.items():
            output.append(
                MetasploitSessionInfo(
                    session_id=session_id,
                    type=details.get("type", ""),
                    session_host=details.get("session_host", ""),
                    tunnel_peer=details.get("tunnel_peer", ""),
                    via_exploit=details.get("via_exploit", ""),
                    via_payload=details.get("via_payload", ""),
                    routes=details.get("routes", ""),
                )
            )

        return output

    # For pivoting, but may not be possible with Incalmo

    def run_post_module(
        self,
        module_fullname: str,
        options: dict[str, Any],
    ) -> MetasploitModuleResult:
        module = self.client.modules.use("post", module_fullname)
        for key, value in options.items():
            module[key] = value

        cid = self.client.consoles.console().cid
        console_output = self.client.consoles.console(cid).run_module_with_output(
            module
        )
        return MetasploitModuleResult(
            console_cid=cid,
            console_output=console_output,
        )

    def autoroute_add(
        self,
        session_id: str,
        subnet: str,
        netmask: str,
    ) -> AutorouteResult:
        result = self.run_post_module(
            module_fullname="multi/manage/autoroute",
            options={
                "SESSION": session_id,
                "CMD": "add",
                "SUBNET": subnet,
                "NETMASK": netmask,
            },
        )
        output = json.dumps(result.model_dump(), indent=2)
        return AutorouteResult(
            session_id=session_id,
            cmd="add",
            subnet=subnet,
            netmask=netmask,
            output=output,
        )

    def autoroute_print(
        self,
        session_id: str,
    ) -> RouteTableResult:
        result = self.run_post_module(
            module_fullname="multi/manage/autoroute",
            options={
                "SESSION": session_id,
                "CMD": "print",
            },
        )
        output = json.dumps(result.model_dump(), indent=2)
        return RouteTableResult(output=output, routes=[])

    def autoroute_delete(
        self,
        session_id: str,
        subnet: str | None = None,
        netmask: str | None = None,
    ) -> AutorouteResult:
        options: dict[str, Any] = {
            "SESSION": session_id,
            "CMD": "delete",
        }
        if subnet is not None:
            options["SUBNET"] = subnet
        if netmask is not None:
            options["NETMASK"] = netmask

        result = self.run_post_module(
            module_fullname="multi/manage/autoroute",
            options=options,
        )
        output = json.dumps(result.model_dump(), indent=2)
        return AutorouteResult(
            session_id=session_id,
            cmd="delete",
            subnet=subnet,
            netmask=netmask,
            output=output,
        )
