from rich.console import Console
from time import sleep

from attacker.Attacker import Attacker
from attacker.config.attacker_config import AttackerConfig, AbstractionLevel
from config.Config import Config
from environment.docker_env import DockerEnv


console = Console()


class DockerEmulator:
    def __init__(
        self,
        config: Config,
        docker_env: DockerEnv,
    ):
        self.config = config
        self.caldera_config = config.caldera_config
        self.docker_env = docker_env

    def start(self, attack_strategy: str):
        c2c_server = f"http://{self.config.external_ip}:8888"
        attacker_config = AttackerConfig(
            name=f"test",
            strategy=attack_strategy,
            environment="EquifaxLarge",
            abstraction=AbstractionLevel.AGENT_LATERAL_MOVE,
            c2c_server=c2c_server,
        )

        attacker = Attacker(
            self.caldera_config.api_key,
            attacker_config,
            attacker_config.name,
        )

        with console.status(
            "Setting up environment...", spinner="dots", spinner_style="green"
        ) as status:
            self.docker_env.setup()

            status.update("Starting attacker server...")
            attacker.wait_for_trusted_agent(timeout=60)

            status.update("Executing attack...")
            attacker.start()

            while True:
                if not attacker.still_running():
                    break
                sleep(5)

            attacker.save_logs("output/test")
