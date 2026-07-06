# database/repositories/integrity_audits.py
from __future__ import annotations

from database.repositories.base import BaseRepository


class IntegrityAuditsRepository(BaseRepository):
    def create_integrity_audit(
        self,
        version_id: int,
        expected_sha256: str,
        observed_sha256: str,
        is_match: bool,
        audited_file_name: str | None,
        audited_file_size_bytes: int | None,
        audited_by: str | None,
        notes: str | None,
        audited_at: str,
    ) -> int:
        return self._execute(
            """
            INSERT INTO integrity_audits (
                version_id, expected_sha256, observed_sha256, is_match,
                audited_file_name, audited_file_size_bytes, audited_by, notes, audited_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                version_id, expected_sha256, observed_sha256, 1 if is_match else 0,
                audited_file_name, audited_file_size_bytes, audited_by, notes, audited_at
            ),
        )

    def list_by_version_id(self, version_id: int) -> list[dict]:
        return self._fetchall(
            """
            SELECT * FROM integrity_audits
            WHERE version_id = ?
            ORDER BY audited_at DESC, id DESC
            """,
            (version_id,),
        )

    def list_recent(self, limit: int = 10) -> list[dict]:
        return self._fetchall(
            f"SELECT * FROM integrity_audits ORDER BY audited_at DESC, id DESC LIMIT {int(limit)}"
        )