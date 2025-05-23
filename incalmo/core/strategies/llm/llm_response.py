# Enum response type
from enum import Enum


class LLMResponseType(Enum):
    QUERY = 0
    ACTION = 1
    FINISHED = 2
    BASH = 3
    MEDIUM_ACTION = 4


class LLMResponse:
    def __init__(self, response_type: LLMResponseType, response: str):
        self.response = response
        self.response_type = response_type
