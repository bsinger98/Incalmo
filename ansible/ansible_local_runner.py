import ansible_runner

from .AnsiblePlaybook import AnsiblePlaybook


class AnsibleLocalRunner:
    def __init__(self, ansible_dir):
        self.ansible_dir = ansible_dir
        self.inventory_path = "ansible/inventory/inventory.local"

    def run_playbook(self, playbook: AnsiblePlaybook):
        playbook_full_params = playbook.params

        ansible_result = ansible_runner.run(
            extravars=playbook_full_params,
            private_data_dir=self.ansible_dir,
            playbook=playbook.name,
            cancel_callback=lambda: None,
        )

        if ansible_result.status == "failed":
            raise Exception(f"Playbook {playbook.name} failed")

    def run_playbooks(self, playbooks: list[AnsiblePlaybook]):
        for playbook in playbooks:
            self.run_playbook(playbook)
