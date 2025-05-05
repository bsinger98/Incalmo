from scenarios.attackers.llm.perry_llms import (
    gpto1_perry,
)
from scenarios.attackers.llm.bash import gpto1_bash


from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    # Perry
    Experiment(
        scenario=Scenario(
            attacker=gpto1_bash,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=1,
    ),
    Experiment(
        scenario=Scenario(
            attacker=gpto1_perry,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=1,
    ),
]
