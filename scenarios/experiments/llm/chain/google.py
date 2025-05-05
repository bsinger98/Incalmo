from scenarios.attackers.llm.perry_llms import (
    gemini1_5_flash_perry,
    gemini1_5_pro_perry,
)
from scenarios.attackers.llm.low_level import (
    gemini1_5_flash_low_level,
    gemini1_5_pro_low_level,
)
from scenarios.attackers.llm.no_services import (
    gemini1_5_flash_no_services,
    gemini1_5_pro_no_services,
)
from scenarios.attackers.llm.bash import gemini1_5_flash_bash, gemini1_5_pro_bash


from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    # Perry
    Experiment(
        scenario=Scenario(
            attacker=gemini1_5_pro_perry,
            defender=absent,
            environment="ChainEnvironment",
        ),
        trials=5,
    ),
    Experiment(
        scenario=Scenario(
            attacker=gemini1_5_flash_perry,
            defender=absent,
            environment="ChainEnvironment",
        ),
        trials=5,
    ),
    # Low Level Actions
    Experiment(
        scenario=Scenario(
            attacker=gemini1_5_pro_low_level,
            defender=absent,
            environment="ChainEnvironment",
        ),
        trials=5,
    ),
    Experiment(
        scenario=Scenario(
            attacker=gemini1_5_flash_low_level,
            defender=absent,
            environment="ChainEnvironment",
        ),
        trials=5,
    ),
    # No services
    Experiment(
        scenario=Scenario(
            attacker=gemini1_5_pro_no_services,
            defender=absent,
            environment="ChainEnvironment",
        ),
        trials=5,
    ),
    Experiment(
        scenario=Scenario(
            attacker=gemini1_5_flash_no_services,
            defender=absent,
            environment="ChainEnvironment",
        ),
        trials=5,
    ),
    # Bash
    Experiment(
        scenario=Scenario(
            attacker=gemini1_5_pro_bash,
            defender=absent,
            environment="ChainEnvironment",
        ),
        trials=5,
    ),
    Experiment(
        scenario=Scenario(
            attacker=gemini1_5_flash_bash,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=5,
    ),
]
