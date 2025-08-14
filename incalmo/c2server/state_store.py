import json
import os
from typing import Any, Optional

from redis import Redis


class StateStore:
    _redis_client: Optional[Redis] = None
    _memory_cache: dict[str, Any] = {"environment:hosts": []}

    @classmethod
    def _get_redis_client(cls) -> Optional[Redis]:
        if cls._redis_client is not None:
            return cls._redis_client

        # Prefer explicit state store URL, then Celery backend/broker, then default
        redis_url = (
            os.environ.get("STATE_REDIS_URL")
            or os.environ.get("result_backend")
            or os.environ.get("broker_url")
            or "redis://localhost:6379/0"
        )

        client = Redis.from_url(redis_url, decode_responses=True)
        # Validate connection
        client.ping()
        cls._redis_client = client
        return cls._redis_client

    @classmethod
    def set_hosts(cls, hosts: list[dict]) -> None:
        client = cls._get_redis_client()
        if client is not None:
            client.set("environment:hosts", json.dumps(hosts))
            return
        cls._memory_cache["environment:hosts"] = hosts

    @classmethod
    def get_hosts(cls) -> list[dict]:
        client = cls._get_redis_client()
        if client is not None:
            data = client.get("environment:hosts")
            if not data:
                return []

            if isinstance(data, (bytes, bytearray)):
                return json.loads(data.decode("utf-8"))
            if isinstance(data, str):
                return json.loads(data)
            # Fallback: attempt to coerce to string
            return json.loads(str(data))

        cached = cls._memory_cache.get("environment:hosts", [])
        return cached if isinstance(cached, list) else []
