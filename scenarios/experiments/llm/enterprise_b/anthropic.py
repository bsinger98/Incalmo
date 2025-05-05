from scenarios.attackers.llm.perry_llms import haiku3_5_perry, sonnet3_5_perry
from scenarios.attackers.llm.low_level import haiku3_5_low_level, sonnet3_5_low_level
from scenarios.attackers.llm.no_services import (
    haiku3_5_no_services,
    sonnet3_5_no_services,
)
from scenarios.attackers.llm.bash import haiku3_5_bash, sonnet3_5_bash


from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    # Perry
    Experiment(
        scenario=Scenario(
            attacker=sonnet3_5_perry,
            defender=absent,
            environment="EnterpriseB",
        ),
        trials=5,
    ),
    Experiment(
        scenario=Scenario(
            attacker=haiku3_5_perry,
            defender=absent,
            environment="EnterpriseB",
        ),
        trials=5,
    ),
    # Low Level Actions
    Experiment(
        scenario=Scenario(
            attacker=sonnet3_5_low_level,
            defender=absent,
            environment="EnterpriseB",
        ),
        trials=5,
    ),
    Experiment(
        scenario=Scenario(
            attacker=haiku3_5_low_level,
            defender=absent,
            environment="EnterpriseB",
        ),
        trials=5,
    ),
    # No services
    Experiment(
        scenario=Scenario(
            attacker=sonnet3_5_no_services,
            defender=absent,
            environment="EnterpriseB",
        ),
        trials=5,
    ),
    Experiment(
        scenario=Scenario(
            attacker=haiku3_5_no_services,
            defender=absent,
            environment="EnterpriseB",
        ),
        trials=5,
    ),
    # Bash
    Experiment(
        scenario=Scenario(
            attacker=sonnet3_5_bash,
            defender=absent,
            environment="EnterpriseB",
        ),
        trials=5,
    ),
    Experiment(
        scenario=Scenario(
            attacker=haiku3_5_bash,
            defender=absent,
            environment="EnterpriseB",
        ),
        trials=5,
    ),
]
