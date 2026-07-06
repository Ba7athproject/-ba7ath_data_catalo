import hashlib
import os
import re
from datetime import datetime


VALID_STATES = {"RAW", "PROCESSING", "CLEAN", "ENRICHED", "PUBLISHED"}
MAX_DATASET_SLUG_LENGTH = 120
MAX_STANDARDIZED_NAME_LENGTH = 200


def slugify_value(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-")


def short_hash(value: str, length: int = 10) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:length]


def truncate_with_hash(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value

    suffix = short_hash(value)
    reserved = len(suffix) + 1
    truncated = value[: max_length - reserved].rstrip("-_")
    return f"{truncated}-{suffix}"


def parse_filename(filename: str) -> dict | None:
    try:
        name_without_ext, _ = os.path.splitext(filename)
        pattern = r"^(\d{8})_([^_]+)_([^_]+)_([^_]+)$"
        match = re.match(pattern, name_without_ext)
        if not match:
            return None

        date_str, source, topic, state = match.groups()
        parsed_date = datetime.strptime(date_str, "%Y%m%d").date()

        return {
            "extraction_date": parsed_date.isoformat(),
            "source": source.replace("-", " "),
            "topic": topic.replace("-", " "),
            "processing_state": state if state in VALID_STATES else "RAW",
        }
    except Exception:
        return None


def build_dataset_slug(source: str, topic: str) -> str:
    raw_slug = slugify_value(f"{source}-{topic}")
    return truncate_with_hash(raw_slug, MAX_DATASET_SLUG_LENGTH)


def build_standardized_name(
    extraction_date: str,
    source: str,
    topic: str,
    processing_state: str,
) -> str:
    date_part = datetime.fromisoformat(extraction_date).strftime("%Y%m%d")
    source_part = slugify_value(source).replace("-", "_")
    topic_part = slugify_value(topic).replace("-", "_")
    state_part = processing_state.upper()

    raw_name = f"{date_part}_{source_part}_{topic_part}_{state_part}"
    return truncate_with_hash(raw_name, MAX_STANDARDIZED_NAME_LENGTH)