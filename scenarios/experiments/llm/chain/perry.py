from scenarios.attackers.llm.perry_llms import haiku3_5_perry, sonnet3_5_perry
from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    Experiment(
        scenario=Scenario(
            attacker=sonnet3_5_perry,
            defender=absent,
            environment="EquifaxLarge",
        ),
        trials=1,
    ),
    Experiment(
        scenario=Scenario(
            attacker=haiku3_5_perry,
            defender=absent,
            environment="EquifaxLarge",
        ),
        trials=1,
    )
]
