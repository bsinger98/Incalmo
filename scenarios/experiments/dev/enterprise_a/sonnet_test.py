from scenarios.attackers.llm.perry_llms import sonnet3_5_perry
from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    Experiment(
        scenario=Scenario(
            attacker=sonnet3_5_perry,
            defender=absent,
            environment="EnterpriseA",
        ),
        trials=1,
    )
]
