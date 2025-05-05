from scenarios.attackers.fsm.graph import sonnet3_5_attacker
from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    # Perry
    Experiment(
        scenario=Scenario(
            attacker=sonnet3_5_attacker,
            defender=absent,
            environment="EquifaxSmall"
        ),
        trials=1,
    )
]
