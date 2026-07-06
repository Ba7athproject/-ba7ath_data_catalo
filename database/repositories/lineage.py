from database.connection import get_connection


class LineageRepository:
    def get_descendant_tree(self, root_version_id: int) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                WITH RECURSIVE lineage AS (
                    SELECT
                        v.id,
                        v.dataset_id,
                        v.version_label,
                        v.standardized_name,
                        v.processing_state,
                        v.parent_version_id,
                        0 AS level
                    FROM dataset_versions v
                    WHERE v.id = ?

                    UNION ALL

                    SELECT
                        child.id,
                        child.dataset_id,
                        child.version_label,
                        child.standardized_name,
                        child.processing_state,
                        child.parent_version_id,
                        lineage.level + 1 AS level
                    FROM dataset_versions child
                    JOIN lineage ON child.parent_version_id = lineage.id
                )
                SELECT *
                FROM lineage
                ORDER BY level ASC, id ASC
                """,
                (root_version_id,),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_ancestors(self, version_id: int) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                WITH RECURSIVE lineage AS (
                    SELECT
                        v.id,
                        v.dataset_id,
                        v.version_label,
                        v.standardized_name,
                        v.processing_state,
                        v.parent_version_id,
                        0 AS level
                    FROM dataset_versions v
                    WHERE v.id = ?

                    UNION ALL

                    SELECT
                        parent.id,
                        parent.dataset_id,
                        parent.version_label,
                        parent.standardized_name,
                        parent.processing_state,
                        parent.parent_version_id,
                        lineage.level + 1 AS level
                    FROM dataset_versions parent
                    JOIN lineage ON lineage.parent_version_id = parent.id
                )
                SELECT *
                FROM lineage
                ORDER BY level ASC
                """,
                (version_id,),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()