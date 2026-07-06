# database/migrations.py
from __future__ import annotations

from database.connection import get_connection

def run_migrations() -> None:
    conn = get_connection()
    try:
        with conn:
            conn.executescript(
                """
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS datasets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slug TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    description TEXT,
                    source_name TEXT NOT NULL,
                    source_url TEXT,
                    source_type TEXT NOT NULL DEFAULT 'unknown',
                    acquisition_vector TEXT NOT NULL,
                    pii_risk_level TEXT NOT NULL DEFAULT 'none',
                    created_by TEXT,
                    collected_by TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS dataset_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER NOT NULL,
                    version_label TEXT NOT NULL,
                    standardized_name TEXT UNIQUE NOT NULL,
                    original_filename TEXT NOT NULL,
                    file_path TEXT,
                    file_size_bytes INTEGER NOT NULL,
                    file_hash_sha256 TEXT NOT NULL,
                    mime_type TEXT,
                    file_extension TEXT,
                    extraction_date TEXT NOT NULL,
                    processing_state TEXT NOT NULL,
                    legal_validation_status INTEGER NOT NULL DEFAULT 0,
                    contains_pii INTEGER NOT NULL DEFAULT 0,
                    processing_steps_json TEXT,
                    ai_details_json TEXT,
                    parent_version_id INTEGER,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
                    FOREIGN KEY (parent_version_id) REFERENCES dataset_versions(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS dataset_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER NOT NULL,
                    version_id INTEGER NOT NULL UNIQUE,
                    row_count INTEGER,
                    column_count INTEGER,
                    null_ratio REAL,
                    duplicate_rows INTEGER,
                    columns_json TEXT,
                    schema_json TEXT,
                    preview_json TEXT,
                    stats_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
                    FOREIGN KEY (version_id) REFERENCES dataset_versions(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS schema_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL UNIQUE,
                    schema_hash TEXT NOT NULL,
                    schema_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (version_id) REFERENCES dataset_versions(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS quality_audits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER NOT NULL,
                    version_id INTEGER NOT NULL,
                    compared_to_version_id INTEGER,
                    quality_score REAL,
                    completeness_score REAL,
                    uniqueness_score REAL,
                    consistency_score REAL,
                    sensitivity_score REAL,
                    row_count INTEGER,
                    column_count INTEGER,
                    null_ratio REAL,
                    duplicate_ratio REAL,
                    sensitive_columns_json TEXT,
                    quality_flags_json TEXT,
                    schema_added_json TEXT,
                    schema_removed_json TEXT,
                    notes TEXT,
                    audited_by TEXT,
                    audit_timestamp TEXT NOT NULL,
                    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
                    FOREIGN KEY (version_id) REFERENCES dataset_versions(id) ON DELETE CASCADE,
                    FOREIGN KEY (compared_to_version_id) REFERENCES dataset_versions(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS integrity_audits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    expected_sha256 TEXT NOT NULL,
                    observed_sha256 TEXT NOT NULL,
                    is_match INTEGER NOT NULL,
                    audited_file_name TEXT,
                    audited_file_size_bytes INTEGER,
                    audited_by TEXT,
                    notes TEXT,
                    audited_at TEXT NOT NULL,
                    FOREIGN KEY (version_id) REFERENCES dataset_versions(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_datasets_slug ON datasets(slug);
                CREATE INDEX IF NOT EXISTS idx_datasets_topic ON datasets(topic);
                CREATE INDEX IF NOT EXISTS idx_datasets_source_name ON datasets(source_name);

                CREATE INDEX IF NOT EXISTS idx_versions_dataset_id ON dataset_versions(dataset_id);
                CREATE INDEX IF NOT EXISTS idx_versions_parent_version_id ON dataset_versions(parent_version_id);
                CREATE INDEX IF NOT EXISTS idx_versions_hash ON dataset_versions(file_hash_sha256);
                CREATE INDEX IF NOT EXISTS idx_versions_standardized_name ON dataset_versions(standardized_name);
                CREATE INDEX IF NOT EXISTS idx_versions_extraction_date ON dataset_versions(extraction_date);

                CREATE INDEX IF NOT EXISTS idx_profiles_dataset_id ON dataset_profiles(dataset_id);
                CREATE INDEX IF NOT EXISTS idx_quality_audits_dataset_id ON quality_audits(dataset_id);
                CREATE INDEX IF NOT EXISTS idx_quality_audits_version_id ON quality_audits(version_id);
                CREATE INDEX IF NOT EXISTS idx_integrity_audits_version_id ON integrity_audits(version_id);
                """
            )
    finally:
        conn.close()