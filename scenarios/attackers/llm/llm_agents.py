from attacker.config.attacker_config import AbstractionLevel
from scenarios.Scenario import AttackerInformation

### Agent LLMs ###
sonnet3_5_agent_scan = AttackerInformation(
    name="Sonnet3.5_agent_scan",
    strategy="sonnet3_5_strategy",
    abstraction=AbstractionLevel.AGENT_SCAN,
)

sonnet3_5_agent_lateral = AttackerInformation(
    name="Sonnet3.5_agent_lateral",
    strategy="sonnet3_5_strategy",
    abstraction=AbstractionLevel.AGENT_LATERAL_MOVE,
)

sonnet3_5_agent_privilege_escalation = AttackerInformation(
    name="Sonnet3.5_agent_privilege_escalation",
    strategy="sonnet3_5_strategy",
    abstraction=AbstractionLevel.AGENT_PRIVILEGE_ESCALATION,
)

sonnet3_5_agent_exfiltration = AttackerInformation(
    name="Sonnet3.5_agent_exfiltration",
    strategy="sonnet3_5_strategy",
    abstraction=AbstractionLevel.AGENT_EXFILTRATE_DATA,
)

sonnet3_5_agent_find_info = AttackerInformation(
    name="Sonnet3.5_agent_find_info",
    strategy="sonnet3_5_strategy",
    abstraction=AbstractionLevel.AGENT_FIND_INFORMATION,
)

sonnet3_5_agent_all = AttackerInformation(
    name="Sonnet3.5_agent_all",
    strategy="sonnet3_5_strategy",
    abstraction=AbstractionLevel.AGENT_ALL,
)
