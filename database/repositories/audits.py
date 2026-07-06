# database/repositories/audits.py
from __future__ import annotations

from database.repositories.base import BaseRepository


class AuditsRepository(BaseRepository):
    def create_quality_audit(
        self,
        dataset_id: int,
        version_id: int,
        compared_to_version_id: int | None,
        quality_score: float | None,
        completeness_score: float | None,
        uniqueness_score: float | None,
        consistency_score: float | None,
        sensitivity_score: float | None,
        row_count: int | None,
        column_count: int | None,
        null_ratio: float | None,
        duplicate_ratio: float | None,
        sensitive_columns_json: str | None,
        quality_flags_json: str | None,
        schema_added_json: str | None,
        schema_removed_json: str | None,
        notes: str | None,
        audited_by: str | None,
        audit_timestamp: str,
    ) -> int:
        return self._execute(
            """
            INSERT INTO quality_audits (
                dataset_id, version_id, compared_to_version_id, quality_score,
                completeness_score, uniqueness_score, consistency_score, sensitivity_score,
                row_count, column_count, null_ratio, duplicate_ratio, sensitive_columns_json,
                quality_flags_json, schema_added_json, schema_removed_json,
                notes, audited_by, audit_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dataset_id, version_id, compared_to_version_id, quality_score,
                completeness_score, uniqueness_score, consistency_score, sensitivity_score,
                row_count, column_count, null_ratio, duplicate_ratio, sensitive_columns_json,
                quality_flags_json, schema_added_json, schema_removed_json,
                notes, audited_by, audit_timestamp
            ),
        )

    def list_quality_audits_by_dataset_id(self, dataset_id: int) -> list[dict]:
        return self._fetchall(
            """
            SELECT * FROM quality_audits
            WHERE dataset_id = ?
            ORDER BY audit_timestamp DESC, id DESC
            """,
            (dataset_id,),
        )

    def list_quality_audits_by_version_id(self, version_id: int) -> list[dict]:
        return self._fetchall(
            """
            SELECT * FROM quality_audits
            WHERE version_id = ?
            ORDER BY audit_timestamp DESC, id DESC
            """,
            (version_id,),
        )

    def list_recent_quality_audits(self, limit: int = 10) -> list[dict]:
        return self._fetchall(
            f"SELECT * FROM quality_audits ORDER BY audit_timestamp DESC, id DESC LIMIT {int(limit)}"
        )