from pydantic import BaseModel
from typing import Dict
from datetime import datetime
import os

import logging
from enum import Enum

# from app.objects.secondclass.c_link import Link
from datetime import datetime


def serialize(self):
    IGNORE_OBJECTS = [logging.Logger]  # , Link]

    dict_format = dict()
    if hasattr(self, "__dict__"):
        for key, value in self.__dict__.items():
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
        return self


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
