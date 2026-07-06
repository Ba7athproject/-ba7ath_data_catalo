# database/repositories/versions.py
from __future__ import annotations

from database.repositories.base import BaseRepository


class VersionsRepository(BaseRepository):
    def create(
        self,
        dataset_id: int,
        version_label: str,
        standardized_name: str,
        original_filename: str,
        file_path: str | None,
        file_size_bytes: int,
        file_hash_sha256: str,
        mime_type: str | None,
        file_extension: str | None,
        extraction_date: str,
        processing_state: str,
        legal_validation_status: bool,
        contains_pii: bool,
        processing_steps_json: str | None,
        ai_details_json: str | None,
        parent_version_id: int | None,
        created_at: str,
    ) -> int:
        return self._execute(
            """
            INSERT INTO dataset_versions (
                dataset_id, version_label, standardized_name, original_filename, file_path,
                file_size_bytes, file_hash_sha256, mime_type, file_extension, extraction_date,
                processing_state, legal_validation_status, contains_pii, processing_steps_json,
                ai_details_json, parent_version_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dataset_id, version_label, standardized_name, original_filename, file_path,
                file_size_bytes, file_hash_sha256, mime_type, file_extension, extraction_date,
                processing_state, 1 if legal_validation_status else 0, 1 if contains_pii else 0,
                processing_steps_json, ai_details_json, parent_version_id, created_at
            ),
        )

    def get_by_id(self, version_id: int) -> dict | None:
        return self._fetchone("SELECT * FROM dataset_versions WHERE id = ?", (version_id,))

    def list_by_dataset_id(self, dataset_id: int) -> list[dict]:
        return self._fetchall(
            "SELECT * FROM dataset_versions WHERE dataset_id = ? ORDER BY id DESC",
            (dataset_id,),
        )

    def count_by_dataset_id(self, dataset_id: int) -> int:
        row = self._fetchone(
            "SELECT COUNT(*) AS cnt FROM dataset_versions WHERE dataset_id = ?",
            (dataset_id,),
        )
        return int(row["cnt"]) if row else 0

    def get_lineage_chain(self, version_id: int) -> list[dict]:
        return self._fetchall(
            """
            WITH RECURSIVE lineage AS (
                SELECT
                    id, dataset_id, version_label, standardized_name,
                    parent_version_id, 0 AS depth
                FROM dataset_versions
                WHERE id = ?

                UNION ALL

                SELECT
                    v.id, v.dataset_id, v.version_label, v.standardized_name,
                    v.parent_version_id, lineage.depth + 1 AS depth
                FROM dataset_versions v
                JOIN lineage ON lineage.parent_version_id = v.id
            )
            SELECT * FROM lineage
            ORDER BY depth DESC
            """,
            (version_id,),
        )