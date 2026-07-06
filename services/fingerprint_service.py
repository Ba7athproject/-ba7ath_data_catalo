import hashlib
import mimetypes
from pathlib import Path


def _reset_stream(file_obj):
    if hasattr(file_obj, "seek"):
        file_obj.seek(0)


def compute_sha256(file_obj) -> str:
    _reset_stream(file_obj)
    file_hash = hashlib.sha256()

    while chunk := file_obj.read(8192):
        file_hash.update(chunk)

    _reset_stream(file_obj)
    return file_hash.hexdigest()


def compute_md5(file_obj) -> str:
    _reset_stream(file_obj)
    file_hash = hashlib.md5()

    while chunk := file_obj.read(8192):
        file_hash.update(chunk)

    _reset_stream(file_obj)
    return file_hash.hexdigest()


def guess_mime_type(filename: str) -> str | None:
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type


def guess_file_format(filename: str) -> str:
    ext = Path(filename).suffix.lower().replace(".", "")
    if ext in {"csv", "xlsx", "json"}:
        return ext
    return ext or "unknown"


def build_fingerprint(uploaded_file) -> dict:
    return {
        "sha256": compute_sha256(uploaded_file),
        "md5": compute_md5(uploaded_file),
        "mime_type": guess_mime_type(uploaded_file.name),
        "file_format": guess_file_format(uploaded_file.name),
        "file_size_bytes": getattr(uploaded_file, "size", None),
    }