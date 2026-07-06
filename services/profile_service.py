import io
import json
from typing import Any

import pandas as pd


SUPPORTED_TABULAR_FORMATS = {"csv", "xlsx", "json"}


def _reset_stream(file_obj):
    if hasattr(file_obj, "seek"):
        file_obj.seek(0)


def read_tabular_preview(uploaded_file, file_format: str) -> pd.DataFrame:
    _reset_stream(uploaded_file)

    if file_format == "csv":
        return pd.read_csv(uploaded_file)

    if file_format == "xlsx":
        return pd.read_excel(uploaded_file)

    if file_format == "json":
        raw = uploaded_file.read()
        _reset_stream(uploaded_file)

        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")

        payload = json.loads(raw)

        if isinstance(payload, list):
            return pd.DataFrame(payload)

        if isinstance(payload, dict):
            if "data" in payload and isinstance(payload["data"], list):
                return pd.DataFrame(payload["data"])
            return pd.json_normalize(payload)

        raise ValueError("Structure JSON non supportée pour le profiling.")

    raise ValueError(f"Format non supporté: {file_format}")


def infer_simple_schema(df: pd.DataFrame) -> list[dict[str, Any]]:
    schema = []
    total_rows = len(df)

    for col in df.columns:
        series = df[col]
        null_count = int(series.isna().sum())
        non_null_count = int(series.notna().sum())
        unique_count = int(series.nunique(dropna=True))

        schema.append({
            "column_name": str(col),
            "dtype": str(series.dtype),
            "null_count": null_count,
            "null_pct": round((null_count / total_rows) * 100, 2) if total_rows else 0.0,
            "non_null_count": non_null_count,
            "unique_count": unique_count,
            "is_unique_candidate": unique_count == non_null_count and non_null_count > 0,
            "sample_values": [
                str(v) for v in series.dropna().astype(str).head(3).tolist()
            ],
        })

    return schema


def build_profile(uploaded_file, file_format: str) -> dict:
    df = read_tabular_preview(uploaded_file, file_format)

    row_count = int(len(df))
    column_count = int(len(df.columns))
    duplicate_rows = int(df.duplicated().sum()) if row_count else 0
    columns = [str(c) for c in df.columns.tolist()]
    schema = infer_simple_schema(df)

    return {
        "row_count": row_count,
        "column_count": column_count,
        "duplicate_rows": duplicate_rows,
        "columns": columns,
        "schema": schema,
        "preview": df.head(20).fillna("").astype(str).to_dict(orient="records"),
    }