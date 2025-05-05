from scenarios.Scenario import AttackerInformation
from attacker.config.attacker_config import LLM

dfs_attacker = AttackerInformation(
    name="DFS",
    strategy="network_DFS",
)

darkside_attacker = AttackerInformation(
    name="Darkside",
    strategy="darkside",
)

sonnet3_5_attacker = AttackerInformation(
    name="LLM", strategy="network_LLM", llm=LLM.SONNET3_5
)
