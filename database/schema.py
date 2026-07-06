SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        topic TEXT NOT NULL,
        description TEXT,
        owner_name TEXT,
        newsroom_project TEXT,
        status_governance TEXT NOT NULL,
        sensitivity_level TEXT NOT NULL,
        legal_review_status TEXT NOT NULL,
        pii_risk_level TEXT NOT NULL,
        source_reliability_score REAL,
        data_quality_score REAL,
        editorial_readiness_score REAL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS dataset_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id INTEGER NOT NULL,
        version_label TEXT NOT NULL,
        parent_version_id INTEGER,
        original_filename TEXT NOT NULL,
        standardized_name TEXT NOT NULL,
        file_path TEXT,
        file_format TEXT NOT NULL,
        mime_type TEXT,
        file_size_bytes INTEGER NOT NULL,
        sha256 TEXT NOT NULL,
        md5 TEXT,
        extraction_date TEXT,
        ingestion_timestamp TEXT NOT NULL,
        acquisition_vector TEXT NOT NULL,
        processing_state TEXT NOT NULL,
        row_count INTEGER,
        column_count INTEGER,
        encoding TEXT,
        delimiter TEXT,
        sheet_names_json TEXT,
        created_by TEXT,
        FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
        FOREIGN KEY (parent_version_id) REFERENCES dataset_versions(id) ON DELETE SET NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id INTEGER NOT NULL,
        source_type TEXT NOT NULL,
        producer_name TEXT,
        source_title TEXT,
        source_url TEXT,
        access_conditions TEXT,
        license_name TEXT,
        jurisdiction TEXT,
        collected_by TEXT,
        collected_at TEXT NOT NULL,
        http_status INTEGER,
        http_headers_json TEXT,
        etag TEXT,
        last_modified TEXT,
        notes TEXT,
        FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_version_id INTEGER NOT NULL,
        profiler_version TEXT,
        row_count INTEGER,
        column_count INTEGER,
        duplicate_rows INTEGER,
        columns_json TEXT,
        schema_json TEXT,
        preview_json TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (dataset_version_id) REFERENCES dataset_versions(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS transformations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version_id INTEGER NOT NULL,
        step_order INTEGER NOT NULL,
        operation_type TEXT NOT NULL,
        tool_name TEXT,
        script_path TEXT,
        prompt_text TEXT,
        model_name TEXT,
        parameters_json TEXT,
        author_type TEXT NOT NULL,
        executed_by TEXT,
        executed_at TEXT NOT NULL,
        notes TEXT,
        FOREIGN KEY (version_id) REFERENCES dataset_versions(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version_id INTEGER NOT NULL,
        audit_type TEXT NOT NULL,
        expected_value TEXT,
        observed_value TEXT,
        status TEXT NOT NULL,
        details_json TEXT,
        audited_at TEXT NOT NULL,
        audited_by TEXT,
        FOREIGN KEY (version_id) REFERENCES dataset_versions(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS dataset_tags (
        dataset_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (dataset_id, tag_id),
        FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_versions_dataset_id
    ON dataset_versions(dataset_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_versions_sha256
    ON dataset_versions(sha256);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_versions_parent_version_id
    ON dataset_versions(parent_version_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_sources_url
    ON sources(source_url);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_datasets_topic
    ON datasets(topic);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_datasets_status_governance
    ON datasets(status_governance);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_audits_version_id
    ON audits(version_id);
    """,
]