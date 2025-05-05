import ansible_runner
import argparse
from rich import print
import time

from typing import Type
from .AnsiblePlaybook import AnsiblePlaybook

from contextlib import redirect_stdout
from os import path

from utility.logging import get_logger

logger = get_logger()


class AnsibleRunner:
    def __init__(self, ssh_key_path, management_ip, ansible_dir, log_path, quiet=False):
        self.ssh_key_path = ssh_key_path
        self.management_ip = management_ip
        self.ansible_dir = ansible_dir
        self.quiet = quiet
        self.log_path = log_path
        self.MAX_RETRIES = 3

        self.ansible_vars_default = {
            "manage_ip": self.management_ip,
            "ssh_key_path": self.ssh_key_path,
        }

    def run_playbook(self, playbook: AnsiblePlaybook):
        if self.quiet is False:
            print(f"\n")
            print(f"[RUNNING PLAYBOOK]    {playbook.name}")
            print(f"[PLAYBOOK  PARAMS]    {playbook.params}")

        log_path = path.join(self.log_path, "ansible_log.log")

        ansible_result = None
        with open(log_path, "a") as f:
            for attempt in range(self.MAX_RETRIES):
                with redirect_stdout(f):
                    # Merge default params with playbook specific params
                    playbook_full_params = self.ansible_vars_default | playbook.params
                    ansible_result = ansible_runner.run(
                        extravars=playbook_full_params,
                        private_data_dir=self.ansible_dir,
                        playbook=playbook.name,
                        cancel_callback=lambda: None,
                        quiet=self.quiet,
                    )
                if ansible_result.status == "successful":
                    break
                else:
                    time.sleep(5)

        if ansible_result is None or ansible_result.status != "successful":
            raise Exception(f"Playbook {playbook.name} failed")

        return ansible_result

    def run_playbooks(self, playbooks: list[AnsiblePlaybook], run_async=True):
        if run_async:
            self.run_playbooks_async(playbooks)
        else:
            self.run_playbooks_serial(playbooks)

    def run_playbooks_serial(self, playbooks: list[AnsiblePlaybook]):
        for playbook in playbooks:
            self.run_playbook(playbook)

    def run_playbooks_async(self, playbooks: list[AnsiblePlaybook]):
        threads = []
        runners = []
        log_path = path.join(self.log_path, "ansible_log.log")
        with open(log_path, "a") as f:
            with redirect_stdout(f):
                # Run max of 10 playbooks at a time
                for i in range(0, len(playbooks), 10):
                    for playbook in playbooks[i : i + 10]:
                        # Merge default params with playbook specific params
                        playbook_full_params = (
                            self.ansible_vars_default | playbook.params
                        )
                        thread, runner = ansible_runner.run_async(
                            extravars=playbook_full_params,
                            private_data_dir=self.ansible_dir,
                            playbook=playbook.name,
                            quiet=False,
                        )
                        threads.append(thread)
                        runners.append(runner)

                    for thread in threads:
                        thread.join()

                    # Check for any failed playbooks
                    for runner in runners:
                        if runner.status == "failed":
                            logger.error(f"Playbook failed")
                            logger.error(f"Playbook Output: {runner.stdout}")
                            logger.error(f"Playbook Error: {runner.stderr}")
                            raise Exception(f"Playbook failed")

    def update_management_ip(self, new_ip):
        self.management_ip = new_ip
        self.ansible_vars_default["manage_ip"] = new_ip
