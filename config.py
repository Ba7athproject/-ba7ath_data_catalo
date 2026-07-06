from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DATABASE_DIR = BASE_DIR / "storage"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATABASE_DIR / "catalog.db"

RAW_STORAGE_DIR = BASE_DIR / "storage" / "raw"
DERIVED_STORAGE_DIR = BASE_DIR / "storage" / "derived"
SNAPSHOTS_STORAGE_DIR = BASE_DIR / "storage" / "snapshots"

EXPORTS_MARKDOWN_DIR = BASE_DIR / "exports" / "markdown"
EXPORTS_REPORTS_DIR = BASE_DIR / "exports" / "reports"
EXPORTS_CHAIN_DIR = BASE_DIR / "exports" / "chain_of_custody"

for path in [
    RAW_STORAGE_DIR,
    DERIVED_STORAGE_DIR,
    SNAPSHOTS_STORAGE_DIR,
    EXPORTS_MARKDOWN_DIR,
    EXPORTS_REPORTS_DIR,
    EXPORTS_CHAIN_DIR,
]:
    path.mkdir(parents=True, exist_ok=True)