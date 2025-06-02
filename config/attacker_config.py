from pydantic import BaseModel
from enum import Enum
from typing import Optional


# Enum of environments
class Environment(Enum):
    EQUIFAX_SMALL = "EquifaxSmall"
    EQUIFAX_MEDIUM = "EquifaxMedium"
    EQUIFAX_LARGE = "EquifaxLarge"
    ICS = "ICSEnvironment"
    RING = "RingEnvironment"
    ENTERPRISE_A = "EnterpriseA"
    ENTERPRISE_B = "EnterpriseB"


class AbstractionLevel(str, Enum):
    INCALMO = "incalmo"
    SHELL = "shell"
    LOW_LEVEL = "low"
    NO_SERVICES = "no_services"
    AGENT_SCAN = "agent_scan"
    AGENT_LATERAL_MOVE = "agent_lateral_move"
    AGENT_PRIVILEGE_ESCALATION = "agent_privilege_escalation"
    AGENT_EXFILTRATE_DATA = "agent_exfiltrate_data"
    AGENT_FIND_INFORMATION = "agent_find_information"
    AGENT_ALL = "agent_all"


class LLM(str, Enum):
    GEMINI1_5 = "gemini1_5"
    GPT4oMINI = "gpt4omini"
    GPT4o = "gpt4o"
    HAIKU3_5 = "haiku3_5"
    SONNET3_5 = "sonnet3_5"


def convert_to_environment(env: str) -> Environment:
    try:
        return Environment(env)
    except ValueError:
        raise ValueError(f"'{env}' is not a valid environment")


def convert_to_abstraction_level(level: str) -> AbstractionLevel:
    try:
        return AbstractionLevel(level)
    except ValueError:
        raise ValueError(f"'{level}' is not a valid level of abstraction")


class AttackerConfig(BaseModel):
    name: str
    strategy: str
    environment: str
    c2c_server: str
    abstraction: Optional[AbstractionLevel] = AbstractionLevel.INCALMO
    llm: Optional[LLM] = None

    class Config:
        # Enums are serialized as their values
        use_enum_values = True
