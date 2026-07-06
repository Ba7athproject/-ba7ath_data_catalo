# database/repositories/datasets.py
from __future__ import annotations

from database.repositories.base import BaseRepository


class DatasetsRepository(BaseRepository):
    def create(
        self,
        slug: str,
        title: str,
        topic: str,
        description: str | None,
        source_name: str,
        source_url: str | None,
        source_type: str,
        acquisition_vector: str,
        pii_risk_level: str,
        created_by: str | None,
        collected_by: str | None,
        created_at: str,
        updated_at: str,
    ) -> int:
        return self._execute(
            """
            INSERT INTO datasets (
                slug, title, topic, description, source_name, source_url, source_type,
                acquisition_vector, pii_risk_level, created_by, collected_by, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                slug, title, topic, description, source_name, source_url, source_type,
                acquisition_vector, pii_risk_level, created_by, collected_by, created_at, updated_at
            ),
        )

    def get_by_id(self, dataset_id: int) -> dict | None:
        return self._fetchone("SELECT * FROM datasets WHERE id = ?", (dataset_id,))

    def get_by_slug(self, slug: str) -> dict | None:
        return self._fetchone("SELECT * FROM datasets WHERE slug = ?", (slug,))

    def list_all(self) -> list[dict]:
        return self._fetchall("SELECT * FROM datasets ORDER BY updated_at DESC, id DESC")

    def update_timestamp(self, dataset_id: int, updated_at: str) -> None:
        self._execute(
            "UPDATE datasets SET updated_at = ? WHERE id = ?",
            (updated_at, dataset_id),
        )