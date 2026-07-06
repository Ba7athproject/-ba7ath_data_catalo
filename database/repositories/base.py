# database/repositories/base.py
from __future__ import annotations

from database.connection import get_db_connection


class BaseRepository:
    def _fetchall(self, query: str, params: tuple = ()) -> list[dict]:
        with get_db_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def _fetchone(self, query: str, params: tuple = ()) -> dict | None:
        with get_db_connection() as conn:
            row = conn.execute(query, params).fetchone()
            return dict(row) if row else None

    def _execute(self, query: str, params: tuple = ()) -> int:
        with get_db_connection() as conn:
            cur = conn.execute(query, params)
            conn.commit()
            return cur.lastrowid

    def _executemany(self, query: str, seq_of_params: list[tuple]) -> None:
        with get_db_connection() as conn:
            conn.executemany(query, seq_of_params)
            conn.commit()