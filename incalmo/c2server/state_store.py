import json
import os
import sqlite3
from typing import Any, Optional


class StateStore:
    TABLE_NAME = "environment"
    DB_PATH = "state_store.db"

    @classmethod
    def initialize(cls) -> None:
        "Delete existing DB file and create a new one."
        if os.path.exists(cls.DB_PATH):
            os.remove(cls.DB_PATH)

    @classmethod
    def _connect(cls) -> sqlite3.Connection:
        return sqlite3.connect(cls.DB_PATH, check_same_thread=False)

    @classmethod
    def set_hosts(cls, hosts: list[dict]) -> None:
        with cls._connect() as conn:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                    host_id TEXT PRIMARY KEY,
                    host TEXT
                )
                """
            )
            for host in hosts:
                conn.execute(
                    f"""
                    INSERT OR REPLACE INTO {cls.TABLE_NAME} (host_id, host)
                    VALUES (?, ?)
                    """,
                    (host.get("host_id"), json.dumps(host)),
                )

    @classmethod
    def get_hosts(cls) -> list[dict]:
        if not os.path.exists(cls.DB_PATH):
            return []
        with cls._connect() as conn:
            try:
                rows = conn.execute(f"SELECT host FROM {cls.TABLE_NAME}").fetchall()
            except sqlite3.OperationalError:
                return []
        return [json.loads(row[0]) for row in rows]
