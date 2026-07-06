# ui/dashboard_dataset_detail.py
from __future__ import annotations

import hashlib
import json
import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st

from database.repositories.catalog import CatalogRepository
from database.repositories.profiles import ProfilesRepository
from database.repositories.audits import AuditsRepository
from database.repositories.integrity_audits import IntegrityAuditsRepository
from database.repositories.versions import VersionsRepository
from ui.components import render_badge


catalog_repo = CatalogRepository()
profiles_repo = ProfilesRepository()
audits_repo = AuditsRepository()
integrity_repo = IntegrityAuditsRepository()
versions_repo = VersionsRepository()


def _safe_json_load(value):
    if not value:
        return []
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return []


def _fmt_dt(value: str | None) -> str:
    if not value:
        return "—"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(value)


def _score_badge(score: float | None) -> tuple[str, str]:
    if score is None:
        return ("Aucun score", "gray")
    if score >= 85:
        return (f"{score}", "green")
    if score >= 70:
        return (f"{score}", "blue")
    if score >= 50:
        return (f"{score}", "orange")
    return (f"{score}", "red")


def _calculate_sha256_from_path(file_path: str) -> str:
    file_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            file_hash.update(chunk)
    return file_hash.hexdigest()


def _save_uploaded_file(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name


def render_dataset_dashboard() -> None:
    st.header("Détail dataset")

    rows = catalog_repo.list_catalog_rows()
    if not rows:
        st.warning("Aucun dataset disponible dans le catalogue.", icon="⚠️")
        return

    dataset_options = {}
    for row in rows:
        label = f'#{row["dataset_id"]} · {row.get("title", "Sans titre")} · {row.get("topic", "Sans sujet")}'
        dataset_options[label] = row["dataset_id"]

    selected_label = st.selectbox("Sélectionner un dataset", list(dataset_options.keys()))
    dataset_id = dataset_options[selected_label]

    detail = catalog_repo.get_dataset_detail(dataset_id)
    if not detail:
        st.error("Impossible de charger le détail du dataset.", icon="❌")
        return

    dataset = detail["dataset"]
    versions = detail.get("versions", [])

    top1, top2, top3, top4 = st.columns(4)
    top1.metric("Dataset ID", dataset.get("id"))
    top2.metric("Slug", dataset.get("slug"))
    top3.metric("Source", dataset.get("source_name"))
    top4.metric("Risque PII", dataset.get("pii_risk_level"))

    st.caption(
        f'Topic: {dataset.get("topic")} · '
        f'Créé le {_fmt_dt(dataset.get("created_at"))} · '
        f'Mis à jour le {_fmt_dt(dataset.get("updated_at"))}'
    )

    if dataset.get("description"):
        st.write(dataset["description"])

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Timeline", "Version & schéma", "Lineage", "Historique audits", "Audit intégrité"]
    )

    with tab1:
        render_version_timeline(versions)

    with tab2:
        render_version_schema_panel(versions)

    with tab3:
        render_lineage_panel(versions)

    with tab4:
        render_audit_history(dataset_id)

    with tab5:
        render_integrity_audit_panel(versions)


def render_version_timeline(versions: list[dict]) -> None:
    st.subheader("Timeline des versions")

    if not versions:
        st.info("Aucune version disponible pour ce dataset.", icon="ℹ️")
        return

    versions_sorted = sorted(versions, key=lambda x: x["id"])

    for idx, version in enumerate(versions_sorted, start=1):
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([1.2, 3, 1.5, 1.5])

            col1.markdown(f"**{version.get('version_label', f'v{idx}')}**")
            col2.code(version.get("standardized_name", "—"))
            col3.write(f"État: {version.get('processing_state', '—')}")
            col4.write(f"Extraction: {_fmt_dt(version.get('extraction_date'))}")

            st.caption(
                f"Version ID #{version.get('id')} · "
                f"Parent version: {version.get('parent_version_id') or '—'} · "
                f"Créé le {_fmt_dt(version.get('created_at'))}"
            )

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Lignes", version.get("row_count") if version.get("row_count") is not None else "—")
            m2.metric("Colonnes", version.get("column_count") if version.get("column_count") is not None else "—")
            m3.metric("Doublons", version.get("duplicate_rows") if version.get("duplicate_rows") is not None else "—")
            m4.metric("Null ratio", version.get("null_ratio") if version.get("null_ratio") is not None else "—")


def render_version_schema_panel(versions: list[dict]) -> None:
    st.subheader("Version, schéma et profil")

    if not versions:
        st.info("Aucune version disponible.", icon="ℹ️")
        return

    selected_version_id = st.selectbox(
        "Choisir une version",
        [v["id"] for v in versions],
        format_func=lambda x: next(
            (
                f'#{v["id"]} · {v.get("version_label", "—")} · {v.get("standardized_name", "—")}'
                for v in versions if v["id"] == x
            ),
            str(x)
        ),
        key="dataset_detail_selected_version",
    )

    version = versions_repo.get_by_id(selected_version_id)
    profile = profiles_repo.get_by_version_id(selected_version_id)
    snapshot = profiles_repo.get_schema_snapshot_by_version_id(selected_version_id)

    if version:
        cmeta1, cmeta2, cmeta3 = st.columns(3)
        cmeta1.metric("Nom standardisé", version.get("standardized_name"))
        cmeta2.metric("Hash SHA-256", (version.get("file_hash_sha256") or "")[:16] + "…")
        cmeta3.metric("Fichier origine", version.get("original_filename") or "—")

        with st.expander("Traçabilité métier", expanded=False):
            st.json(
                {
                    "processing_steps_json": _safe_json_load(version.get("processing_steps_json")),
                    "ai_details_json": _safe_json_load(version.get("ai_details_json")),
                    "contains_pii": version.get("contains_pii"),
                    "parent_version_id": version.get("parent_version_id"),
                    "file_path": version.get("file_path"),
                }
            )

    if not profile:
        st.info("Aucun profil enregistré pour cette version.", icon="ℹ️")
        return

    columns = _safe_json_load(profile.get("columns_json"))
    schema = _safe_json_load(profile.get("schema_json"))
    preview = _safe_json_load(profile.get("preview_json"))
    stats = _safe_json_load(profile.get("stats_json"))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lignes", profile.get("row_count"))
    c2.metric("Colonnes", profile.get("column_count"))
    c3.metric("Doublons", profile.get("duplicate_rows"))
    c4.metric("Null ratio", profile.get("null_ratio"))

    with st.expander("Colonnes détectées", expanded=False):
        if columns:
            st.json(columns)
        else:
            st.caption("Aucune colonne disponible.")

    with st.expander("Schéma détaillé", expanded=True):
        if schema:
            st.dataframe(schema, use_container_width=True)
        else:
            st.caption("Aucun schéma détaillé disponible.")

    with st.expander("Aperçu des données", expanded=False):
        if preview:
            st.dataframe(preview, use_container_width=True)
        else:
            st.caption("Aucun aperçu disponible.")

    with st.expander("Stats techniques", expanded=False):
        st.json(stats if stats else {})

    with st.expander("Schema snapshot", expanded=False):
        if snapshot:
            st.json(
                {
                    "version_id": snapshot.get("version_id"),
                    "schema_hash": snapshot.get("schema_hash"),
                    "created_at": snapshot.get("created_at"),
                }
            )
        else:
            st.caption("Aucun snapshot de schéma enregistré.")


def render_lineage_panel(versions: list[dict]) -> None:
    st.subheader("Lineage")

    if not versions:
        st.info("Aucun lineage disponible.", icon="ℹ️")
        return

    latest_version = sorted(versions, key=lambda x: x["id"], reverse=True)[0]
    lineage = versions_repo.get_lineage_chain(latest_version["id"])

    if not lineage:
        st.caption("Aucune chaîne de lineage disponible.")
        return

    st.markdown("**Chaîne reconstituée parent → enfant**")
    for item in lineage:
        depth = item.get("depth", 0)
        indent = "&nbsp;" * 6 * depth
        st.markdown(
            f"{indent}➡️ **{item.get('version_label', '—')}** — "
            f"`{item.get('standardized_name', '—')}`",
            unsafe_allow_html=True,
        )


def render_audit_history(dataset_id: int) -> None:
    st.subheader("Historique des audits qualité")

    audits = audits_repo.list_quality_audits_by_dataset_id(dataset_id)
    if not audits:
        st.info("Aucun audit qualité enregistré.", icon="ℹ️")
        return

    for audit in audits:
        score_label, score_color = _score_badge(audit.get("quality_score"))

        with st.expander(
            f'Audit #{audit["id"]} · Version #{audit["version_id"]} · {_fmt_dt(audit["audit_timestamp"])}',
            expanded=False,
        ):
            render_badge(f"Score global: {score_label}", color=score_color)

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Complétude", audit.get("completeness_score"))
            c2.metric("Unicité", audit.get("uniqueness_score"))
            c3.metric("Cohérence", audit.get("consistency_score"))
            c4.metric("Sensibilité", audit.get("sensitivity_score"))
            c5.metric("Null ratio", audit.get("null_ratio"))

            c6, c7, c8 = st.columns(3)
            c6.metric("Lignes", audit.get("row_count"))
            c7.metric("Colonnes", audit.get("column_count"))
            c8.metric("Duplicate ratio", audit.get("duplicate_ratio"))

            sensitive_columns = _safe_json_load(audit.get("sensitive_columns_json"))
            quality_flags = _safe_json_load(audit.get("quality_flags_json"))
            schema_added = _safe_json_load(audit.get("schema_added_json"))
            schema_removed = _safe_json_load(audit.get("schema_removed_json"))

            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("**Drapeaux qualité**")
                if quality_flags:
                    for flag in quality_flags:
                        st.warning(flag, icon="⚠️")
                else:
                    st.success("Aucun drapeau critique.", icon="✅")

                st.markdown("**Colonnes sensibles**")
                if sensitive_columns:
                    st.json(sensitive_columns)
                else:
                    st.caption("Aucune colonne sensible détectée.")

            with col_b:
                st.markdown("**Diff de schéma**")
                st.markdown("Colonnes ajoutées")
                if schema_added:
                    st.json(schema_added)
                else:
                    st.caption("Aucune")

                st.markdown("Colonnes supprimées")
                if schema_removed:
                    st.json(schema_removed)
                else:
                    st.caption("Aucune")

            if audit.get("notes"):
                st.markdown("**Notes**")
                st.write(audit["notes"])


def render_integrity_audit_panel(versions: list[dict]) -> None:
    st.subheader("Certification et vérification de l’empreinte")
    st.markdown(
        "Déposez un fichier présent sur votre machine pour vérifier s’il a subi des altérations "
        "par rapport à sa déclaration officielle."
    )

    if not versions:
        st.warning("Aucune version disponible pour audit d’intégrité.", icon="⚠️")
        return

    selected_version_id = st.selectbox(
        "1. Choisir la référence dans le Carnet de Bord",
        [v["id"] for v in versions],
        format_func=lambda x: next(
            (
                f'#{v["id"]} · {v.get("standardized_name", "—")}'
                for v in versions if v["id"] == x
            ),
            str(x)
        ),
        key="integrity_selected_version",
    )

    target_version = versions_repo.get_by_id(selected_version_id)
    if not target_version:
        st.error("Version introuvable.", icon="❌")
        return

    audit_file = st.file_uploader(
        "2. Déposer le fichier physique à tester",
        type=["csv", "tsv", "xlsx", "xls", "json"],
        key="uploader_audit_integrity_v2",
    )

    audited_by = st.text_input("Audité par", key="integrity_audited_by")
    notes = st.text_area("Notes audit intégrité", key="integrity_notes", height=90)

    if audit_file is None:
        integrity_history = integrity_repo.list_by_version_id(selected_version_id)
        if integrity_history:
            st.markdown("### Historique des audits d’intégrité")
            for item in integrity_history:
                with st.expander(
                    f'Audit #{item["id"]} · {_fmt_dt(item["audited_at"])} · '
                    f'{"MATCH" if item["is_match"] else "MISMATCH"}',
                    expanded=False,
                ):
                    st.json(item)
        return

    if st.button("Lancer l’audit d’intégrité"):
        temp_path = None
        try:
            with st.spinner("Calcul de l’empreinte actuelle..."):
                temp_path = _save_uploaded_file(audit_file)
                current_hash = _calculate_sha256_from_path(temp_path)

            expected_hash = target_version["file_hash_sha256"]
            is_match = current_hash == expected_hash

            integrity_repo.create_integrity_audit(
                version_id=selected_version_id,
                expected_sha256=expected_hash,
                observed_sha256=current_hash,
                is_match=is_match,
                audited_file_name=audit_file.name,
                audited_file_size_bytes=getattr(audit_file, "size", None),
                audited_by=audited_by.strip() or None,
                notes=notes.strip() or None,
                audited_at=datetime.now().isoformat(),
            )

            st.markdown("### Résultat de l’analyse")
            if is_match:
                st.success(
                    "INTÉGRITÉ CONFIRMÉE — le fichier est strictement identique à sa version d’origine.",
                    icon="✅",
                )
                st.info(f"Hash certifié SHA-256 : {current_hash}")
            else:
                st.error(
                    "ALERTE — modification détectée, les empreintes numériques ne correspondent pas.",
                    icon="🚨",
                )

                colh1, colh2 = st.columns(2)
                with colh1:
                    st.warning(f"Empreinte attendue : {expected_hash}")
                with colh2:
                    st.error(f"Empreinte observée : {current_hash}")

        except Exception as exc:
            st.exception(exc)
        finally:
            if temp_path:
                try:
                    Path(temp_path).unlink(missing_ok=True)
                except Exception:
                    pass

    integrity_history = integrity_repo.list_by_version_id(selected_version_id)
    if integrity_history:
        st.markdown("### Historique des audits d’intégrité")
        for item in integrity_history:
            with st.expander(
                f'Audit #{item["id"]} · {_fmt_dt(item["audited_at"])} · '
                f'{"MATCH" if item["is_match"] else "MISMATCH"}',
                expanded=False,
            ):
                st.json(item)