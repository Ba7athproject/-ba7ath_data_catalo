# database/repositories/catalog.py
from __future__ import annotations

from database.repositories.base import BaseRepository


class CatalogRepository(BaseRepository):
    def list_catalog_rows(self) -> list[dict]:
        return self._fetchall(
            """
            SELECT
                d.id AS dataset_id,
                d.slug,
                d.title,
                d.topic,
                d.description,
                d.source_name,
                d.source_url,
                d.source_type,
                d.acquisition_vector,
                d.pii_risk_level,
                d.created_at AS dataset_created_at,
                d.updated_at AS dataset_updated_at,
                v.id AS version_id,
                v.version_label,
                v.standardized_name,
                v.original_filename,
                v.file_path,
                v.file_size_bytes,
                v.file_hash_sha256,
                v.extraction_date,
                v.processing_state,
                v.legal_validation_status,
                v.contains_pii,
                v.parent_version_id,
                v.created_at AS version_created_at,
                p.row_count,
                p.column_count,
                p.null_ratio,
                p.duplicate_rows
            FROM datasets d
            LEFT JOIN dataset_versions v ON d.id = v.dataset_id
            LEFT JOIN dataset_profiles p ON v.id = p.version_id
            ORDER BY d.updated_at DESC, v.id DESC
            """
        )

    def get_dataset_detail(self, dataset_id: int) -> dict | None:
        dataset = self._fetchone("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
        if not dataset:
            return None

        versions = self._fetchall(
            """
            SELECT
                v.*,
                p.row_count,
                p.column_count,
                p.null_ratio,
                p.duplicate_rows
            FROM dataset_versions v
            LEFT JOIN dataset_profiles p ON v.id = p.version_id
            WHERE v.dataset_id = ?
            ORDER BY v.id DESC
            """,
            (dataset_id,),
        )

        return {
            "dataset": dataset,
            "versions": versions,
        }