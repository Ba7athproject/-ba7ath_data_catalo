from database.connection import get_connection


class SourcesRepository:
    def create_source(
        self,
        dataset_id: int,
        source_type: str,
        collected_at: str,
        producer_name: str | None = None,
        source_title: str | None = None,
        source_url: str | None = None,
        access_conditions: str | None = None,
        license_name: str | None = None,
        jurisdiction: str | None = None,
        collected_by: str | None = None,
        http_status: int | None = None,
        http_headers_json: str | None = None,
        etag: str | None = None,
        last_modified: str | None = None,
        notes: str | None = None,
    ) -> int:
        conn = get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO sources (
                    dataset_id, source_type, producer_name, source_title, source_url,
                    access_conditions, license_name, jurisdiction, collected_by,
                    collected_at, http_status, http_headers_json, etag,
                    last_modified, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dataset_id,
                    source_type,
                    producer_name,
                    source_title,
                    source_url,
                    access_conditions,
                    license_name,
                    jurisdiction,
                    collected_by,
                    collected_at,
                    http_status,
                    http_headers_json,
                    etag,
                    last_modified,
                    notes,
                ),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def list_by_dataset_id(self, dataset_id: int) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT *
                FROM sources
                WHERE dataset_id = ?
                ORDER BY collected_at DESC
                """,
                (dataset_id,),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()