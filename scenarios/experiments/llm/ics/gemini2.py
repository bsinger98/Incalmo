from scenarios.attackers.llm.perry_llms import (
    gemini2_flash_perry,
)
from scenarios.attackers.llm.bash import gemini2_flash_bash
from scenarios.attackers.llm.no_services import gemini2_flash_no_services
from scenarios.attackers.llm.low_level import gemini2_flash_low_level


from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    # Perry
    Experiment(
        scenario=Scenario(
            attacker=gemini2_flash_perry,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=4,
    ),
    Experiment(
        scenario=Scenario(
            attacker=gemini2_flash_no_services,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=5,
    ),
    Experiment(
        scenario=Scenario(
            attacker=gemini2_flash_low_level,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=5,
    ),
    Experiment(
        scenario=Scenario(
            attacker=gemini2_flash_bash,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=4,
    ),
]
