import os

from environment.terraform_helpers import deploy_network, destroy_network
from config.Config import LLMAPIKeys


class DockerEnv:
    def __init__(self, name: str, llm_api_keys: LLMAPIKeys):
        self.name = name
        self.llm_api_keys = llm_api_keys

    def setup(self, fresh=True):
        topology_path = os.path.join("docker", self.name)

        if fresh:
            self.teardown()
        deploy_network(topology_path, False, self.llm_api_keys)

    def teardown(self):
        topology_path = os.path.join("docker", self.name)
        destroy_network(topology_path, False)
