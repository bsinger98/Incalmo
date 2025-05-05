from pydantic import BaseModel
from typing import Optional


class ElasticSearchConfig(BaseModel):
    api_key: str
    port: int


class CalderaConfig(BaseModel):
    api_key: str
    port: int
    external: bool = True
    python_path: str = ""
    caldera_path: str = ""


class OpenstackConfig(BaseModel):
    ssh_key_name: str
    ssh_key_path: str


class LLMAPIKeys(BaseModel):
    open_ai: str = ""
    anthropic: str = ""
    google: str = ""


class Config(BaseModel):
    elastic_config: ElasticSearchConfig
    caldera_config: CalderaConfig
    openstack_config: OpenstackConfig
    external_ip: str
    experiment_timeout_minutes: int
    llm_api_keys: Optional[LLMAPIKeys]
