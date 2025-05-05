from scenarios.attackers.testers.enterprise_a import enterprise_a_tester
from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    Experiment(
        scenario=Scenario(
            attacker=enterprise_a_tester,
            defender=absent,
            environment="EnterpriseA",
        ),
        trials=5,
    )
]
