from scenarios.defenders.absent import absent
from scenarios.defenders.layered import layered_d10_h10
from scenarios.defenders.reactive import reactive_layered_d10_h10

from scenarios.attackers.fsm.graph import dfs_attacker, darkside_attacker

from scenarios.generators import generate_experiments

attackers = [
    dfs_attacker,
    darkside_attacker,
]

defenders = [
    absent,
    layered_d10_h10,
    reactive_layered_d10_h10,
]

environments = [
    "EnterpriseA",
    "ChainEnvironment",
    "Star",
    "EnterpriseA",
    "EquifaxLarge",
    "ICSEnvironment",
    # "PEChainEnvironment",
    # "Dumbbell",
    # "DumbbellPE",
    # "EnterpriseB",
    # "StarPE",
]


experiment = generate_experiments(attackers, defenders, environments, trials=3)
