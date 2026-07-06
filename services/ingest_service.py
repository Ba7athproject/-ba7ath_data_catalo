# services/ingest_service.py
from __future__ import annotations

import hashlib
import json
import mimetypes
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from database.repositories.datasets import DatasetsRepository
from database.repositories.versions import VersionsRepository
from database.repositories.profiles import ProfilesRepository


class IngestService:
    PROCESSING_STATES = {"RAW", "PROCESSING", "CLEAN"}

    def __init__(self) -> None:
        self.datasets_repo = DatasetsRepository()
        self.versions_repo = VersionsRepository()
        self.profiles_repo = ProfilesRepository()

    def parse_filename(self, filename: str) -> dict | None:
        """
        Reprend et étend la logique du prototype :
        YYYYMMDD_source_sujet_etat.ext
        """
        try:
            name_without_ext = Path(filename).stem
            pattern = r"^(\d{8})_([^_]+)_([^_]+)_([^_]+)$"
            match = re.match(pattern, name_without_ext)
            if not match:
                return None

            date_str, source_name, topic, processing_state = match.groups()
            parsed_date = datetime.strptime(date_str, "%Y%m%d").date()

            return {
                "extraction_date": parsed_date.isoformat(),
                "source_name": source_name.replace("-", " "),
                "topic": topic.replace("-", " "),
                "processing_state": (
                    processing_state if processing_state in self.PROCESSING_STATES else "RAW"
                ),
            }
        except Exception:
            return None

    def build_standardized_name(
        self,
        extraction_date: str,
        source_name: str,
        topic: str,
        processing_state: str,
        version_label: str | None = None,
    ) -> str:
        date_part = datetime.fromisoformat(extraction_date).strftime("%Y%m%d")
        source_part = self._slug_fragment(source_name or "INCONNUE")
        topic_part = self._slug_fragment(topic or "SANS-NOM")
        state_part = (processing_state or "RAW").upper()

        base = f"{date_part}_{source_part}_{topic_part}_{state_part}"
        if version_label:
            return f"{base}_{self._slug_fragment(version_label)}"
        return base

    def build_dataset_slug(self, title: str, source_name: str, topic: str) -> str:
        raw = f"{title}-{source_name}-{topic}"
        return self._slug_fragment(raw)

    def calculate_sha256_from_path(self, file_path: str) -> str:
        file_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                file_hash.update(chunk)
        return file_hash.hexdigest()

    def ingest_file(
        self,
        file_path: str,
        title: str,
        topic: str,
        source_name: str,
        source_url: str | None,
        source_type: str,
        acquisition_vector: str,
        pii_risk_level: str,
        description: str | None,
        created_by: str | None,
        collected_by: str | None,
        processing_state: str,
        parent_version_id: int | None,
        legal_validation_status: bool,
        contains_pii: bool,
        processing_steps: list[str] | None,
        ai_details: dict | None,
        extraction_date: str,
    ) -> dict:
        now = self._now_iso()

        dataset_slug = self.build_dataset_slug(title, source_name, topic)
        dataset = self.datasets_repo.get_by_slug(dataset_slug)

        if dataset is None:
            dataset_id = self.datasets_repo.create(
                slug=dataset_slug,
                title=title.strip(),
                topic=topic.strip(),
                description=description.strip() if description else None,
                source_name=source_name.strip(),
                source_url=source_url.strip() if source_url else None,
                source_type=source_type,
                acquisition_vector=acquisition_vector,
                pii_risk_level=pii_risk_level,
                created_by=created_by.strip() if created_by else None,
                collected_by=collected_by.strip() if collected_by else None,
                created_at=now,
                updated_at=now,
            )
            dataset = self.datasets_repo.get_by_id(dataset_id)
        else:
            dataset_id = dataset["id"]
            self.datasets_repo.update_timestamp(dataset_id, now)
            dataset = self.datasets_repo.get_by_id(dataset_id)

        version_count = self.versions_repo.count_by_dataset_id(dataset_id)
        version_label = f"v{version_count + 1}"

        standardized_name = self.build_standardized_name(
            extraction_date=extraction_date,
            source_name=source_name,
            topic=topic,
            processing_state=processing_state,
            version_label=version_label,
        )

        file_hash_sha256 = self.calculate_sha256_from_path(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        file_extension = Path(file_path).suffix.lower().replace(".", "") or None
        file_size_bytes = Path(file_path).stat().st_size

        profiling = self.profile_file(file_path)
        schema_hash = self.compute_schema_hash(profiling["schema"])

        version_id = self.versions_repo.create(
            dataset_id=dataset_id,
            version_label=version_label,
            standardized_name=standardized_name,
            original_filename=Path(file_path).name,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            file_hash_sha256=file_hash_sha256,
            mime_type=mime_type,
            file_extension=file_extension,
            extraction_date=extraction_date,
            processing_state=processing_state,
            legal_validation_status=legal_validation_status,
            contains_pii=contains_pii,
            processing_steps_json=json.dumps(processing_steps or [], ensure_ascii=False),
            ai_details_json=json.dumps(ai_details or {}, ensure_ascii=False),
            parent_version_id=parent_version_id,
            created_at=now,
        )

        profile_id = self.profiles_repo.create_profile(
            dataset_id=dataset_id,
            version_id=version_id,
            row_count=profiling["row_count"],
            column_count=profiling["column_count"],
            null_ratio=profiling["null_ratio"],
            duplicate_rows=profiling["duplicate_rows"],
            columns_json=json.dumps(profiling["columns"], ensure_ascii=False),
            schema_json=json.dumps(profiling["schema"], ensure_ascii=False),
            preview_json=json.dumps(profiling["preview"], ensure_ascii=False),
            stats_json=json.dumps(profiling["stats"], ensure_ascii=False),
            created_at=now,
        )

        schema_snapshot_id = self.profiles_repo.create_schema_snapshot(
            version_id=version_id,
            schema_hash=schema_hash,
            schema_json=json.dumps(profiling["schema"], ensure_ascii=False),
            created_at=now,
        )

        return {
            "dataset": self.datasets_repo.get_by_id(dataset_id),
            "version": self.versions_repo.get_by_id(version_id),
            "profiling": profiling,
            "profile_id": profile_id,
            "schema_snapshot_id": schema_snapshot_id,
        }

    def profile_file(self, file_path: str) -> dict:
        df = self._read_dataframe(file_path)

        row_count = int(len(df))
        column_count = int(len(df.columns))
        duplicate_rows = int(df.duplicated().sum()) if row_count > 0 else 0

        total_cells = max(row_count * max(column_count, 1), 1)
        null_cells = int(df.isna().sum().sum()) if row_count > 0 else 0
        null_ratio = round(null_cells / total_cells, 4)

        columns = [str(col) for col in df.columns.tolist()]
        schema = []
        stats = {}

        for col in df.columns:
            series = df[col]
            dtype = str(series.dtype)
            null_count = int(series.isna().sum())
            unique_count = int(series.nunique(dropna=True))

            schema.append(
                {
                    "name": str(col),
                    "dtype": dtype,
                    "null_count": null_count,
                    "null_ratio": round((null_count / max(row_count, 1)), 4),
                    "unique_count": unique_count,
                    "sample_values": self._sample_values(series, limit=5),
                }
            )

        stats = {
            "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
            "duplicate_rows": duplicate_rows,
            "total_cells": total_cells,
            "null_cells": null_cells,
        }

        preview = df.head(20).astype(object).where(pd.notnull(df.head(20)), None).to_dict(orient="records")

        return {
            "row_count": row_count,
            "column_count": column_count,
            "null_ratio": null_ratio,
            "duplicate_rows": duplicate_rows,
            "columns": columns,
            "schema": schema,
            "preview": preview,
            "stats": stats,
        }

    def compute_schema_hash(self, schema: list[dict]) -> str:
        payload = json.dumps(schema, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _read_dataframe(self, file_path: str) -> pd.DataFrame:
        suffix = Path(file_path).suffix.lower()

        if suffix == ".csv":
            return pd.read_csv(file_path)
        if suffix == ".tsv":
            return pd.read_csv(file_path, sep="\t")
        if suffix in {".xlsx", ".xls"}:
            return pd.read_excel(file_path)
        if suffix == ".json":
            try:
                return pd.read_json(file_path)
            except ValueError:
                return pd.json_normalize(json.loads(Path(file_path).read_text(encoding="utf-8")))

        raise ValueError(f"Format non supporté : {suffix}")

    def _sample_values(self, series: pd.Series, limit: int = 5) -> list:
        values = series.dropna().astype(str).head(limit).tolist()
        return values

    def _slug_fragment(self, value: str) -> str:
        value = value.strip().lower()
        value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
        value = re.sub(r"[\s_]+", "-", value)
        value = re.sub(r"-{2,}", "-", value)
        return value.strip("-") or "na"

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()