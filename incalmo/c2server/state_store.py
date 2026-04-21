import json
import os
import sqlite3
from typing import Any, Optional


class StateStore:
    TABLE_NAME = "environment"
    DB_PATH = "state_store.db"
    _db_connection: Optional[sqlite3.Connection] = None

    @classmethod
    def initialize(cls) -> None:
        "Delete existing DB file and create a new one."
        if os.path.exists(cls.DB_PATH):
            os.remove(cls.DB_PATH)

    @classmethod
    def set_hosts(cls, hosts: list[dict]) -> None:
        conn = sqlite3.connect(cls.DB_PATH, check_same_thread=False)
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                    host_id TEXT PRIMARY KEY,
                    host TEXT
                )
                """
            )
            for host in hosts:
                host_id = host.get("host_id") or host.get("hostname", "unknown")
                cursor.execute(
                    f"""
                    INSERT OR REPLACE INTO {cls.TABLE_NAME} (host_id, host)
                    VALUES (?, ?)
                    """,
                    (host_id, json.dumps(host)),
                )
            conn.commit()
        finally:
            conn.close()

    @classmethod
    def get_hosts(cls) -> list[dict]:
        if not os.path.exists(cls.DB_PATH):
            return []

        conn = sqlite3.connect(cls.DB_PATH, check_same_thread=False)
        try:
            cursor = conn.cursor()
            try:
                cursor.execute(f"SELECT host from {cls.TABLE_NAME}")
            except sqlite3.OperationalError:
                # Table does not exist yet
                return []
            rows = cursor.fetchall()
            return [json.loads(row[0]) for row in rows]
        finally:
            conn.close()
