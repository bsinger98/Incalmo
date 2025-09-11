from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
import os

import logging
from enum import Enum

from datetime import datetime


def serialize(obj: Any):
    from incalmo.core.strategies.llm.interfaces.llm_agent_interface import (
        LLMAgentInterface,
    )

    IGNORE_OBJECTS = [logging.Logger, LLMAgentInterface]

    dict_format = dict()
    dict_format["class_name"] = obj.__class__.__name__

    if hasattr(obj, "__dict__"):
        # Add class name to the serialized object
        for key, value in obj.__dict__.items():
            if type(value) in IGNORE_OBJECTS:
                continue
            elif isinstance(value, Enum):
                dict_format[key] = value.value
            elif isinstance(value, datetime):
                dict_format[key] = value.isoformat()
            elif isinstance(value, list):
                if value and type(value[0]) in IGNORE_OBJECTS:
                    continue
                else:
                    dict_format[key] = [serialize(item) for item in value]
            elif isinstance(value, dict):
                dict_format[key] = {str(k): serialize(v) for k, v in value.items()}
            else:
                dict_format[key] = serialize(value)
        return dict_format
    else:
        return obj


class HighLevelActionLog(BaseModel):
    operation_id: str
    timestamp: datetime
    action: str
    action_params: dict
    action_results: Dict[str, dict]


class LowLevelActionLog(BaseModel):
    operation_id: str
    timestamp: datetime
    action: str
    action_params: dict
    action_results: Dict[str, dict]
