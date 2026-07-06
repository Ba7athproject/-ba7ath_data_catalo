# services/quality_audit_service.py
from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from database.repositories.audits import AuditsRepository
from database.repositories.profiles import ProfilesRepository
from database.repositories.versions import VersionsRepository


class QualityAuditService:
    SENSITIVE_PATTERNS = [
        r"\bname\b",
        r"\bfull_name\b",
        r"\bfirst_name\b",
        r"\blast_name\b",
        r"\bemail\b",
        r"\bphone\b",
        r"\bmobile\b",
        r"\baddress\b",
        r"\bpassport\b",
        r"\bnational_id\b",
        r"\bcin\b",
        r"\bssn\b",
        r"\bib an\b",
        r"\biban\b",
        r"\bbank\b",
        r"\bdob\b",
        r"\bbirth\b",
        r"\bgps\b",
        r"\blat\b",
        r"\blon\b",
        r"\bgeo\b",
    ]

    def __init__(self) -> None:
        self.audits_repo = AuditsRepository()
        self.profiles_repo = ProfilesRepository()
        self.versions_repo = VersionsRepository()

    def run_and_persist_audit(
        self,
        dataset_id: int,
        version_id: int,
        audited_by: str | None = None,
        compared_to_version_id: int | None = None,
        notes: str | None = None,
    ) -> dict:
        profile = self.profiles_repo.get_by_version_id(version_id)
        if not profile:
            raise ValueError(f"Aucun profil trouvé pour version_id={version_id}")

        current_schema = self._load_json(profile.get("schema_json")) or []
        current_columns = self._load_json(profile.get("columns_json")) or []

        row_count = profile.get("row_count") or 0
        column_count = profile.get("column_count") or 0
        null_ratio = float(profile.get("null_ratio") or 0)
        duplicate_rows = int(profile.get("duplicate_rows") or 0)

        completeness_score = round(max(0, 100 - (null_ratio * 100)), 2)
        uniqueness_score = self._compute_uniqueness_score(row_count, duplicate_rows)
        consistency_score = self._compute_consistency_score(current_schema)
        sensitive_columns = self.detect_sensitive_columns(current_columns)
        sensitivity_score = self._compute_sensitivity_score(sensitive_columns)

        quality_flags = self.generate_quality_flags(
            row_count=row_count,
            column_count=column_count,
            null_ratio=null_ratio,
            duplicate_rows=duplicate_rows,
            sensitive_columns=sensitive_columns,
        )

        schema_added = []
        schema_removed = []

        if compared_to_version_id:
            previous_profile = self.profiles_repo.get_by_version_id(compared_to_version_id)
            if previous_profile:
                previous_columns = self._load_json(previous_profile.get("columns_json")) or []
                schema_added, schema_removed = self.diff_columns(previous_columns, current_columns)

        duplicate_ratio = round((duplicate_rows / max(row_count, 1)), 4)

        quality_score = round(
            (
                completeness_score * 0.35
                + uniqueness_score * 0.25
                + consistency_score * 0.25
                + sensitivity_score * 0.15
            ),
            2,
        )

        audit_payload = {
            "dataset_id": dataset_id,
            "version_id": version_id,
            "compared_to_version_id": compared_to_version_id,
            "quality_score": quality_score,
            "completeness_score": completeness_score,
            "uniqueness_score": uniqueness_score,
            "consistency_score": consistency_score,
            "sensitivity_score": sensitivity_score,
            "row_count": row_count,
            "column_count": column_count,
            "null_ratio": null_ratio,
            "duplicate_ratio": duplicate_ratio,
            "sensitive_columns_json": json.dumps(sensitive_columns, ensure_ascii=False),
            "quality_flags_json": json.dumps(quality_flags, ensure_ascii=False),
            "schema_added_json": json.dumps(schema_added, ensure_ascii=False),
            "schema_removed_json": json.dumps(schema_removed, ensure_ascii=False),
            "notes": notes,
            "audited_by": audited_by,
            "audit_timestamp": self._now_iso(),
        }

        audit_id = self.audits_repo.create_quality_audit(**audit_payload)
        audit_payload["id"] = audit_id
        audit_payload["sensitive_columns"] = sensitive_columns
        audit_payload["quality_flags"] = quality_flags
        audit_payload["schema_added"] = schema_added
        audit_payload["schema_removed"] = schema_removed
        return audit_payload

    def detect_sensitive_columns(self, columns: list[str]) -> list[str]:
        matches = []
        for col in columns:
            normalized = str(col).strip().lower()
            for pattern in self.SENSITIVE_PATTERNS:
                if re.search(pattern, normalized):
                    matches.append(col)
                    break
        return sorted(set(matches))

    def diff_columns(self, old_columns: list[str], new_columns: list[str]) -> tuple[list[str], list[str]]:
        old_set = set(old_columns)
        new_set = set(new_columns)
        added = sorted(list(new_set - old_set))
        removed = sorted(list(old_set - new_set))
        return added, removed

    def generate_quality_flags(
        self,
        row_count: int,
        column_count: int,
        null_ratio: float,
        duplicate_rows: int,
        sensitive_columns: list[str],
    ) -> list[str]:
        flags = []

        if row_count == 0:
            flags.append("Dataset vide.")
        if column_count == 0:
            flags.append("Aucune colonne détectée.")
        if null_ratio >= 0.50:
            flags.append("Taux de valeurs manquantes très élevé.")
        elif null_ratio >= 0.20:
            flags.append("Taux de valeurs manquantes significatif.")
        if duplicate_rows > 0:
            flags.append(f"{duplicate_rows} ligne(s) dupliquée(s) détectée(s).")
        if sensitive_columns:
            flags.append("Colonnes potentiellement sensibles détectées.")
        return flags

    def _compute_uniqueness_score(self, row_count: int, duplicate_rows: int) -> float:
        if row_count <= 0:
            return 0.0
        ratio = duplicate_rows / row_count
        return round(max(0, 100 - (ratio * 100)), 2)

    def _compute_consistency_score(self, schema: list[dict]) -> float:
        if not schema:
            return 0.0

        penalties = 0
        for col in schema:
            dtype = str(col.get("dtype", "")).lower()
            name = str(col.get("name", "")).strip()
            if not name:
                penalties += 10
            if dtype == "object":
                penalties += 2

        score = max(0, 100 - penalties)
        return round(score, 2)

    def _compute_sensitivity_score(self, sensitive_columns: list[str]) -> float:
        if not sensitive_columns:
            return 100.0
        penalty = min(len(sensitive_columns) * 10, 60)
        return round(max(0, 100 - penalty), 2)

    def _load_json(self, value):
        if not value:
            return []
        if isinstance(value, (list, dict)):
            return value
        try:
            return json.loads(value)
        except Exception:
            return []

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()