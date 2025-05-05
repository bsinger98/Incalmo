from scenarios.attackers.fsm.graph import dfs_attacker 
from scenarios.Scenario import Scenario, Experiment
from scenarios.Scenario import DefenderInformation

llm_defense = DefenderInformation(
    name="LLMDefense1",
    telemetry="SimpleTelemetryAnalysis",
    strategy="LLMStrategy1",
    capabilities={
        "DeployDecoy": 10,
        "HoneyService": 0,
        "RestoreServer": -1,
        "HoneyCredentials": 50,
    },
)

experiment = [
    # Perry
    Experiment(
        scenario=Scenario(
            attacker=dfs_attacker,
            defender=llm_defense,
            environment="EquifaxLarge",
        ),
        trials=5,
    ),
]
