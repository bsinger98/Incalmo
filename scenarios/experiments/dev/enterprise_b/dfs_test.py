from scenarios.attackers.fsm.graph import dfs_attacker
from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    Experiment(
        scenario=Scenario(
            attacker=dfs_attacker,
            defender=absent,
            environment="EnterpriseB",
        ),
        trials=1,
    )
]
