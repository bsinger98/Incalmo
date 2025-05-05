from scenarios.attackers.llm.llm_agents import sonnet3_5_agent_scan


from scenarios.defenders.absent import absent
from scenarios.generators import generate_experiments


# Example usage:
attackers = [sonnet3_5_agent_scan]
defenders = [absent]
environments = [
    "EquifaxLarge",
    # "ICSEnvironment",
    # "ChainEnvironment",
    # "PEChainEnvironment",
    # "Dumbbell",
    # "DumbbellPE",
    # "EnterpriseA",
    # "EnterpriseB",
    # "Star",
    # "StarPE",
]

experiment = generate_experiments(attackers, defenders, environments, trials=5)
