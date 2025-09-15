import json
import os
from typing import Any, Optional


class StateStore:
    _memory_cache: dict[str, Any] = {"environment:hosts": []}

    @classmethod
    def set_hosts(cls, hosts: list[dict]) -> None:
        cls._memory_cache["environment:hosts"] = hosts

    @classmethod
    def get_hosts(cls) -> list[dict]:
        cached = cls._memory_cache.get("environment:hosts", [])
        return cached if isinstance(cached, list) else []
