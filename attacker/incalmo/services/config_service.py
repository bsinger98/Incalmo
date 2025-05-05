import os
import json
from plugins.deception.app.data.attacker_config import AttackerConfig

CONFIG_PATH = "plugins/deception/app/data/config.json"


class ConfigService:

    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        # Check if config.json exists
        if not os.path.exists(CONFIG_PATH):
            raise FileNotFoundError("config.json not found")

        # Load config.json
        with open(CONFIG_PATH, "r") as f:
            config = f.read()
            json_config = json.loads(config)

        return AttackerConfig(**json_config)

    def get_config(self):
        return self.config
