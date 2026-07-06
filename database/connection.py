# database/connection.py
from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path("catalog.db")
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_db_connection() as conn:
        conn.executescript(schema_sql)