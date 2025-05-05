from scenarios.attackers.llm.bash import sonnet3_5_bash
from scenarios.defenders.absent import absent
from scenarios.defenders.layered import layered_d10_h10
from scenarios.defenders.reactive import reactive_layered_d10_h10
from scenarios.defenders.static import static_d10
from scenarios.Scenario import Scenario, Experiment

experiment = [
    # Perry
    Experiment(
        scenario=Scenario(
            attacker=sonnet3_5_bash,
            defender=absent,
            environment="Chain2Hosts",
        ),
        trials=10,
    ),
    Experiment(
      scenario=Scenario(
        attacker=sonnet3_5_bash,
        defender=layered_d10_h10,
        environment="Chain2Hosts",
      ),
      trials=10,
    ),
    Experiment(
      scenario=Scenario(
        attacker=sonnet3_5_bash,
        defender=reactive_layered_d10_h10,
        environment="Chain2Hosts",
      ),
      trials=10,
    ),
    Experiment(
      scenario=Scenario(
        attacker=sonnet3_5_bash,
        defender=static_d10,
        environment="Chain2Hosts",
      ),
      trials=10,
    ),
]
