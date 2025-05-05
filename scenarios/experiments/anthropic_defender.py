from scenarios.attackers.llm.perry_llms import haiku3_5_perry, sonnet3_5_perry
from scenarios.defenders.naive import naive
from scenarios.Scenario import Scenario, Experiment

experiment = [
    # Perry
    Experiment(
        scenario=Scenario(
            attacker=sonnet3_5_perry,
            defender=naive,
            environment="EquifaxSmall",
        ),
        trials=2,
    ),
    Experiment(
        scenario=Scenario(
            attacker=haiku3_5_perry,
            defender=naive,
            environment="EquifaxSmall",
        ),
        trials=2,
    ),
]
