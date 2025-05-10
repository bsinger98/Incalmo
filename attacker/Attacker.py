from time import sleep
import requests
from utility.logging.logging import PerryLogger
from datetime import datetime
import subprocess
import os
import psutil


from attacker.config.attacker_config import AttackerConfig
from attacker.exceptions import NoAttackerAgentsError, AttackerServerDownError


class Attacker:
    def __init__(
        self,
        caldera_api_key: str,
        config: AttackerConfig,
        operation_id=None,
    ):
        self.caldera_api_key = caldera_api_key
        self.caldera_process = None
        self.config = config

        if operation_id is not None:
            self.operation_id = operation_id
        else:
            # Use timestamp as operation_id
            cur_time = datetime.now()
            self.operation_id = cur_time.strftime("%Y-%m-%d %H:%M:%S")

        self.api_headers = {
            "key": self.caldera_api_key,
            "Content-Type": "application/json",
        }
        return

    def kill_existing_caldera(self):
        # Find and terminate any running Caldera server processes
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            if proc and proc.info:
                cmdline = proc.info["cmdline"]
                # Check if the process matches the Caldera server
                if cmdline and "server.py" in cmdline:
                    proc.terminate()  # Send a SIGTERM
                    proc.wait(timeout=5)  # Wait for process to terminate

    def start_server(self, caldera_python_env, caldera_path):
        self.kill_existing_caldera()

        # Start Caldera
        self.caldera_process = subprocess.Popen(
            [caldera_python_env, "server.py", "--insecure", "--fresh"],
            cwd=caldera_path,
            stdout=PerryLogger.caldera_log_file,
            stderr=subprocess.STDOUT,
        )

        # Wait 10s for caldera server to turn on
        sleep(10)

    def stop_server(self):
        if self.caldera_process is not None:
            self.caldera_process.terminate()

    def start_operation(self):
        # Clear old agents if they exist
        self.delete_agents()

        # Wait for a trusted agent to appear
        self.wait_for_trusted_agent()

        # Send attacker config
        requests.post(
            "http://localhost:8888/plugin/deception/initial_parameters",
            headers=self.api_headers,
            json=self.config.model_dump_json(),
        )

        json_data = {
            "name": self.config.name,
            "id": self.operation_id,
            "adversary": {
                "adversary_id": "deception_enterprise",
            },
            "planner": {
                "id": self.config.strategy,
            },
            "source": {
                "id": "ed32b9c3-9593-4c33-b0db-e2007315096b",
            },
        }

        requests.post(
            "http://localhost:8888/api/v2/operations",
            headers=self.api_headers,
            json=json_data,
        )

    def stop_operation(self):
        # Send patch request
        json_data = {"state": "stop"}
        response = requests.patch(
            f"http://localhost:8888/api/v2/operations/{self.operation_id}",
            headers=self.api_headers,
            json=json_data,
        )

    def get_operation_details(self):
        response = requests.get(
            f"http://localhost:8888/api/v2/operations/{self.operation_id}",
            headers=self.api_headers,
        )
        operation_details = response.json()

        return operation_details

    def get_llm_logs(self):
        response = requests.get(
            f"http://localhost:8888/plugin/deception/get_logs/{self.operation_id}",
            headers=self.api_headers,
        )
        return response.json()

    def save_logs(self, output_dir):
        logs = self.get_llm_logs()
        llm_log = logs["llm"]
        perry_log = logs["perry"]
        low_level_action_log = logs["low_level_action"]
        high_level_action_log = logs["high_level_action"]
        pre_prompt = logs["preprompt"]
        bash_log = logs["bash"]

        if llm_log is not None:
            with open(os.path.join(output_dir, "llm_log.log"), "w") as f:
                f.write(llm_log)

        if perry_log is not None:
            with open(os.path.join(output_dir, "perry_attacker.log"), "w") as f:
                f.write(perry_log)

        if low_level_action_log is not None:
            with open(os.path.join(output_dir, "low_level_action.json"), "w") as f:
                f.write(low_level_action_log)

        if high_level_action_log is not None:
            with open(os.path.join(output_dir, "high_level_action.json"), "w") as f:
                f.write(high_level_action_log)

        if pre_prompt is not None:
            with open(os.path.join(output_dir, "pre_prompt.log"), "w") as f:
                f.write(pre_prompt)

        if bash_log is not None:
            with open(os.path.join(output_dir, "bash.log"), "w") as f:
                f.write(bash_log)

    def still_running(self):
        operation_details = self.get_operation_details()
        if operation_details["state"] == "running":
            return True

        return False

    def get_facts(self):
        response = requests.get(
            f"http://localhost:8888/api/v2/facts/{self.operation_id}",
            headers=self.api_headers,
        )
        raw_json = response.json()

        return raw_json["found"]

    def get_relationships(self):
        response = requests.get(
            f"http://localhost:8888/api/v2/relationships/{self.operation_id}",
            headers=self.api_headers,
        )
        raw_json = response.json()

        return raw_json["found"]

    def get_agents(self):
        response = requests.get(
            f"http://localhost:8888/api/v2/agents", headers=self.api_headers
        )
        response_json = response.json()
        return response_json

    def delete_agents(self):
        agents = self.get_agents()
        for agent in agents:
            if agent["trusted"] is False:
                resp = requests.delete(
                    f"http://localhost:8888/api/v2/agents/{agent['paw']}",
                    headers=self.api_headers,
                )
        return

    def start(self):
        try:
            self.delete_agents()
            self.start_operation()
        except requests.exceptions.ConnectionError:
            raise AttackerServerDownError("Caldera server is down")

    def wait_for_trusted_agent(self, timeout=10):
        for i in range(timeout):
            # Wait for agent to check in
            try:
                agents = self.get_agents()
                for agent in agents:
                    if agent["trusted"] is True:
                        return agent["paw"]
            except requests.exceptions.ConnectionError:
                pass

            sleep(1)

        raise NoAttackerAgentsError("Timeout waiting for agent to check in")

    def cleanup(self):
        self.delete_agents()

        self.stop_server()
        return
