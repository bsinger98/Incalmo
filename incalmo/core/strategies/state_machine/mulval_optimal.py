"""
MulvalOptimal — oracle attacker that executes the MulVAL-optimal attack plan.

Loads the pre-computed plan AND the MHBench environment spec at startup.
Uses known host IPs and data file paths directly, so no network scanning or
credential discovery is needed — every action is issued with exact parameters.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from config.attacker_config import AttackerConfig
from incalmo.core.actions.high_level_action import HighLevelAction
from incalmo.core.actions.HighLevel import ExfiltrateData
from incalmo.core.actions.LowLevel import (
    ExploitStruts,
    NCLateralMove,
    SSHLateralMove,
    SudoBaronExploit,
    WriteablePasswdExploit,
)
from incalmo.core.models.events import ServicesDiscoveredOnHost
from incalmo.core.models.network import Host
from incalmo.models.agent import Agent
from incalmo.core.services import (
    AttackGraphService,
    EnvironmentStateService,
    LowLevelActionOrchestrator,
)
from incalmo.core.services.action_context import HighLevelContext
from incalmo.core.strategies.incalmo_strategy import IncalmoStrategy

_PLAN_DIR = Path("/home/cyberautonomy/v3_MHBench/mulval/graphs")
_ENV_DIR = Path("/home/cyberautonomy/v3_MHBench/environments")

_ENV_STEMS: dict[str, str] = {
    "EquifaxSmall": "equifax_small",
    "EquifaxMedium": "equifax_medium",
    "EquifaxLarge": "equifax_large",
    "ICSEnvironment": "ics",
    "EnterpriseA": "enterprise_a",
    "EnterpriseB": "enterprise_b",
}


# ── env / plan loading ────────────────────────────────────────────────────────


def _env_to_stem(env_name: str) -> str:
    bare = env_name.split("/")[-1]
    return _ENV_STEMS.get(bare) or re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", bare).lower()


def _load_plan(env_name: str) -> list[dict]:
    stem = _env_to_stem(env_name)
    return json.loads((_PLAN_DIR / f"{stem}_plan.json").read_text())["steps"]


def _load_env_state(env_name: str) -> dict:
    stem = _env_to_stem(env_name)
    path = _PLAN_DIR / f"{stem}_state.json"
    return json.loads(path.read_text()) if path.exists() else {}


def _load_env_spec(env_name: str) -> dict:
    bare = env_name.split("/")[-1]
    for path in _ENV_DIR.rglob(f"{bare}.json"):
        return json.loads(path.read_text())
    raise FileNotFoundError(f"Environment spec not found for {env_name!r}")


def _parse_env_spec(
    spec: dict,
) -> tuple[dict[str, str], dict[str, dict[str, list[str]]]]:
    """Extract host IPs and data file paths from the MHBench environment spec.

    Returns:
        host_ips:   {logical_name → ip_address}
        data_files: {logical_name → {user → [file_path, ...]}}
    """
    host_ips: dict[str, str] = {}
    data_files: dict[str, dict[str, list[str]]] = {}

    for network in spec.get("networks", []):
        for subnet in network.get("subnets", []):
            for host in subnet.get("hosts", []):
                if "ip_address" in host:
                    host_ips[host["name"]] = host["ip_address"]

    for pb in spec.get("playbooks", []):
        if pb["name"] == "add_data":
            args = pb["args"]
            host = args["host"]
            user = args["host_user"]
            fpath = args["path"]
            data_files.setdefault(host, {}).setdefault(user, []).append(fpath)

    return host_ips, data_files


# ── thin HL wrapper for running a single LL action ────────────────────────────


class _RunLL(HighLevelAction):
    """Wraps a low-level action so it can be run through the HL orchestrator."""

    def __init__(self, ll_action):
        super().__init__()
        self._ll = ll_action

    async def run(
        self,
        ll_orch: LowLevelActionOrchestrator,
        env_service: EnvironmentStateService,
        ag_service: AttackGraphService,
        ctx: HighLevelContext,
    ):
        return await ll_orch.run_action(self._ll, ctx)


# ── strategy ──────────────────────────────────────────────────────────────────


class MulvalOptimal(IncalmoStrategy, name="MulvalOptimal"):
    """Execute the MulVAL-optimal attack plan with oracle knowledge of the environment."""

    def __init__(
        self,
        config: AttackerConfig,
        logger: str = "incalmo",
        task_id: str = "",
    ):
        super().__init__(config, logger, task_id)
        self._plan = _load_plan(config.environment)
        spec = _load_env_spec(config.environment)
        self._host_ips, self._data_files = _parse_env_spec(spec)
        self._env_state = _load_env_state(config.environment)
        self._cursor = 0
        self._state_populated = False

    # ── main loop ─────────────────────────────────────────────────────────────

    async def step(self) -> bool:
        if not self._state_populated:
            self._pre_populate_state()
            self._state_populated = True
        if self._cursor >= len(self._plan):
            return True
        plan_step = self._plan[self._cursor]
        self._cursor += 1
        await self._execute(plan_step)
        return False

    # ── step dispatch ─────────────────────────────────────────────────────────

    async def _execute(self, step: dict) -> None:
        action = step["action"]
        technique = step.get("technique")

        if action == "lateral_move":
            src_agent = self._get_agent(step["source_host"], step.get("source_user"))
            tgt_ip = self._host_ips.get(step["target_host"])
            if src_agent is None or tgt_ip is None:
                return

            if technique == "struts":
                ll = ExploitStruts(src_agent, tgt_ip, "8080")
            elif technique == "ssh":
                tgt_user = step.get("target_user")
                dest = f"{tgt_user}@{tgt_ip}" if tgt_user else tgt_ip
                ll = SSHLateralMove(src_agent, dest)
            elif technique == "netcat":
                ll = NCLateralMove(src_agent, tgt_ip, "4444")
            else:
                return

            await self.high_level_action_orchestrator.run_action(_RunLL(ll))

        elif action == "privesc":
            src_agent = self._get_agent(step["target_host"])
            if src_agent is None:
                return

            if technique == "sudobaron":
                ll = SudoBaronExploit(src_agent)
            elif technique == "writeable":
                ll = WriteablePasswdExploit(src_agent)
            else:
                return

            await self.high_level_action_orchestrator.run_action(_RunLL(ll))

        elif action == "exfiltrate":
            host = self._resolve(step["target_host"])
            if host is None:
                return
            # Pre-populate known data file paths (no FindInformationOnAHost needed)
            if not host.critical_data_files:
                host.critical_data_files = self._data_files.get(step["target_host"], {})
            await self.high_level_action_orchestrator.run_action(ExfiltrateData(host))

    # ── state pre-population ──────────────────────────────────────────────────

    def _pre_populate_state(self) -> None:
        """Register known host services in the ESS using oracle env spec data.

        Called once before the first plan step so that high-level actions like
        ExfiltrateData see the correct service topology without scanning.
        """
        for ip, services in self._env_state.get("host_services", {}).items():
            self.environment_state_service.handle_ServicesDiscoveredOnHost(
                ServicesDiscoveredOnHost(
                    host_ip=ip,
                    services={int(port): svc for port, svc in services.items()},
                )
            )

    # ── helpers ───────────────────────────────────────────────────────────────

    def _get_agent(
        self, logical_name: str | None, username: str | None = None
    ) -> Agent | None:
        host = self._resolve(logical_name)
        if host is None:
            return None
        if username:
            return host.get_agent_by_username(username)
        return host.get_agent()

    def _resolve(self, logical_name: str | None) -> Host | None:
        """Find a live Host by IP address from the env spec (authoritative)."""
        if not logical_name:
            return None
        spec_ip = self._host_ips.get(logical_name)
        if not spec_ip:
            return None
        for host in self.environment_state_service.network.get_all_hosts():
            if spec_ip in (host.ip_addresses or []):
                return host
        return None


def _normalize(name: str) -> str:
    return name.lower().replace("-", "_")
