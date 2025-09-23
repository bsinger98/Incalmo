import json
import os
import sqlite3
from typing import Any, Optional

class StateStore:
    TABLE_NAME = "environment"
    DB_PATH = "state_store.db"

    @classmethod
    def set_hosts(cls, hosts: list[dict]) -> None:
        cls._db_connection = sqlite3.connect(cls.DB_PATH)
        cursor = cls._db_connection.cursor()
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                host_id TEXT PRIMARY KEY,
                host TEXT
            )
            """
        )
        for host in hosts:
            cursor.execute(
                f"""
                INSERT OR REPLACE INTO {cls.TABLE_NAME} (host_id, host)
                VALUES (?, ?)
                """,
                (host.get("host_id"), json.dumps(host)),
            )
        cls._db_connection.commit()

    @classmethod
    def get_hosts(cls) -> list[dict]:
        if cls._db_connection is None:
            cls._db_connection = sqlite3.connect(cls.DB_PATH)
        cursor = cls._db_connection.cursor()
        cursor.execute(f"SELECT host from {cls.TABLE_NAME}")
        rows = cursor.fetchall()
        cls._db_connection.commit()
        return [json.loads(row[0]) for row in rows]
