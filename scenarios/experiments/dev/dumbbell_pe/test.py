from scenarios.attackers.testers.dumbbell_pe_tester import dumbbell_pe_tester
from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    Experiment(
        scenario=Scenario(
            attacker=dumbbell_pe_tester,
            defender=absent,
            environment="DumbbellPE",
        ),
        trials=5,
    )
]
