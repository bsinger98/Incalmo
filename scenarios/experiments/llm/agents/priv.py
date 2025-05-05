from scenarios.attackers.llm.llm_agents import (
    sonnet3_5_agent_privilege_escalation,
    sonnet3_5_agent_scan,
    sonnet3_5_agent_lateral,
    sonnet3_5_agent_exfiltration,
    sonnet3_5_agent_find_info,
    sonnet3_5_agent_all,
)


from scenarios.defenders.absent import absent
from scenarios.generators import generate_experiments


# Example usage:
attackers = [
    sonnet3_5_agent_privilege_escalation,
    sonnet3_5_agent_scan,
    sonnet3_5_agent_lateral,
    sonnet3_5_agent_exfiltration,
    sonnet3_5_agent_find_info,
    sonnet3_5_agent_all,
]
defenders = [absent]
environments = [
    # "EquifaxLarge",
    # "ICSEnvironment",
    # "ChainEnvironment",
    # "PEChainEnvironment",
    # "Dumbbell",
    # "DumbbellPE",
    # "EnterpriseA",
    # "EnterpriseB",
    # "Star",
    "StarPE",
]

experiment = generate_experiments(attackers, defenders, environments, trials=5)
