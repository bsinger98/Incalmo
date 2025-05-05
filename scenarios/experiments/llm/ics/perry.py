from scenarios.attackers.llm.perry_llms import (
    haiku3_5_perry,
    sonnet3_5_perry,
    gpt4o_perry,
    gpt4o_mini_perry,
    gemini1_5_pro_perry,
    gemini1_5_flash_perry,
)
from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    Experiment(
        scenario=Scenario(
            attacker=haiku3_5_perry,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=1,
    ),
    Experiment(
        scenario=Scenario(
            attacker=sonnet3_5_perry,
            defender=absent,
            environment="ICSEnvironment",
        ),
        trials=1,
    ),
    # Experiment(
    #     scenario=Scenario(
    #         attacker=gpt4o_mini_perry,
    #         defender=absent,
    #         environment="ICSEnvironment",
    #     ),
    #     trials=1,
    # ),
    # Experiment(
    #     scenario=Scenario(
    #         attacker=gpt4o_perry,
    #         defender=absent,
    #         environment="ICSEnvironment",
    #     ),
    #     trials=1,
    # ),
    # Experiment(
    #     scenario=Scenario(
    #         attacker=gemini1_5_pro_perry,
    #         defender=absent,
    #         environment="ICSEnvironment",
    #     ),
    #     trials=1,
    # ),
    # Experiment(
    #     scenario=Scenario(
    #         attacker=gemini1_5_flash_perry,
    #         defender=absent,
    #         environment="ICSEnvironment",
    #     ),
    #     trials=1,
    # ),
]
