from dataclasses import dataclass
from typing import Optional
from openstack.connection import Connection

from ansible.AnsibleRunner import AnsibleRunner
from attacker.Attacker import Attacker
from environment.environment import Environment
from config.Config import Config
from emulator.emulator import Emulator


@dataclass
class PerryContext:
    config: Config

    # Openstack experiment context
    openstack_conn = None
    ansible_runner = None
    experiment_dir = None
    experiment_id = None

    # Set by cli modules
    emulator: Optional[Emulator] = None
    environment: Optional[Environment] = None
    attacker: Optional[Attacker] = None
