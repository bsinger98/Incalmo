from scenarios.attackers.llm.perry_llms import haiku3_5_perry, sonnet3_5_perry
from scenarios.defenders.reactive import reactive
from scenarios.Scenario import Scenario, Experiment

experiment = [
    # Perry
    Experiment(
        scenario=Scenario(
            attacker=sonnet3_5_perry,
            defender=reactive,
            environment="EquifaxSmall",
        ),
        trials=3,
    ),
]
