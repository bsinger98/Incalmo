import ansible_runner

from .AnsiblePlaybook import AnsiblePlaybook


class AnsibleDockerRunner:
    def __init__(self, ansible_dir):
        self.ansible_dir = ansible_dir
        self.inventory_path = "inventories/inventory.docker"

    def run_playbook(self, playbook: AnsiblePlaybook):
        playbook_full_params = playbook.params
        print(self.inventory_path)
        print(playbook.name)

        ansible_result = ansible_runner.run(
            extravars=playbook_full_params,
            private_data_dir=self.ansible_dir,
            # inventory=self.inventory_path,
            playbook=playbook.name,
            cancel_callback=lambda: None,
        )

        if ansible_result.status == "failed":
            raise Exception(f"Playbook {playbook.name} failed")

    def run_playbooks(self, playbooks: list[AnsiblePlaybook]):
        for playbook in playbooks:
            self.run_playbook(playbook)
