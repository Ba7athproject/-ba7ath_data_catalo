# database/repositories/profiles.py
from __future__ import annotations

from database.repositories.base import BaseRepository


class ProfilesRepository(BaseRepository):
    def create_profile(
        self,
        dataset_id: int,
        version_id: int,
        row_count: int | None,
        column_count: int | None,
        null_ratio: float | None,
        duplicate_rows: int | None,
        columns_json: str | None,
        schema_json: str | None,
        preview_json: str | None,
        stats_json: str | None,
        created_at: str,
    ) -> int:
        return self._execute(
            """
            INSERT INTO dataset_profiles (
                dataset_id, version_id, row_count, column_count, null_ratio,
                duplicate_rows, columns_json, schema_json, preview_json, stats_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dataset_id, version_id, row_count, column_count, null_ratio,
                duplicate_rows, columns_json, schema_json, preview_json, stats_json, created_at
            ),
        )

    def get_by_version_id(self, version_id: int) -> dict | None:
        return self._fetchone(
            "SELECT * FROM dataset_profiles WHERE version_id = ?",
            (version_id,),
        )

    def create_schema_snapshot(
        self,
        version_id: int,
        schema_hash: str,
        schema_json: str | None,
        created_at: str,
    ) -> int:
        return self._execute(
            """
            INSERT INTO schema_snapshots (version_id, schema_hash, schema_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (version_id, schema_hash, schema_json, created_at),
        )

    def get_schema_snapshot_by_version_id(self, version_id: int) -> dict | None:
        return self._fetchone(
            "SELECT * FROM schema_snapshots WHERE version_id = ?",
            (version_id,),
        )