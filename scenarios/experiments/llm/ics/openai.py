from scenarios.attackers.llm.perry_llms import (
    gpt4o_mini_perry,
    gpt4o_perry,
)
from scenarios.attackers.llm.low_level import (
    gpt4o_mini_low_level,
    gpt4o_low_level,
)
from scenarios.attackers.llm.no_services import (
    gpt4o_mini_no_services,
    gpt4o_no_services,
)
from scenarios.attackers.llm.bash import gpt4o_mini_bash, gpt4o_bash


from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    # Perry
    Experiment(
        scenario=Scenario(
            attacker=gpt4o_perry,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=5,
    ),
    Experiment(
        scenario=Scenario(
            attacker=gpt4o_mini_perry,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=5,
    ),
    # Low Level Actions
    Experiment(
        scenario=Scenario(
            attacker=gpt4o_low_level,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=5,
    ),
    Experiment(
        scenario=Scenario(
            attacker=gpt4o_mini_low_level,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=5,
    ),
    # No services
    Experiment(
        scenario=Scenario(
            attacker=gpt4o_no_services,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=5,
    ),
    Experiment(
        scenario=Scenario(
            attacker=gpt4o_mini_no_services,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=5,
    ),
    # Bash
    Experiment(
        scenario=Scenario(
            attacker=gpt4o_bash,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=5,
    ),
    Experiment(
        scenario=Scenario(
            attacker=gpt4o_mini_bash,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=5,
    ),
]
