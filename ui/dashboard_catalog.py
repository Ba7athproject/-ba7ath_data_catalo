# ui/dashboard_catalog.py
from __future__ import annotations

from datetime import datetime
import pandas as pd
import streamlit as st

from database.repositories.catalog import CatalogRepository
from database.repositories.versions import VersionsRepository
from database.repositories.audits import AuditsRepository
from database.repositories.integrity_audits import IntegrityAuditsRepository


catalog_repo = CatalogRepository()
versions_repo = VersionsRepository()
audits_repo = AuditsRepository()
integrity_repo = IntegrityAuditsRepository()


def _fmt_dt(value: str | None) -> str:
    if not value:
        return "—"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(value)


def _bool_to_flag(value) -> str:
    if value in (1, True, "1", "true", "True"):
        return "Oui"
    if value in (0, False, "0", "false", "False"):
        return "Non"
    return "—"


def _safe_num(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _build_catalog_dataframe(rows: list[dict]) -> pd.DataFrame:
    normalized = []
    for row in rows:
        normalized.append(
            {
                "dataset_id": row.get("dataset_id"),
                "version_id": row.get("version_id"),
                "titre": row.get("title"),
                "topic": row.get("topic"),
                "source": row.get("source_name"),
                "type_source": row.get("source_type"),
                "etat": row.get("processing_state"),
                "version_label": row.get("version_label"),
                "nom_standardise": row.get("standardized_name"),
                "date_extraction": row.get("extraction_date"),
                "created_at": row.get("version_created_at"),
                "taille_octets": row.get("file_size_bytes"),
                "lignes": row.get("row_count"),
                "colonnes": row.get("column_count"),
                "null_ratio": row.get("null_ratio"),
                "doublons": row.get("duplicate_rows"),
                "pii": _bool_to_flag(row.get("contains_pii")),
                "risque_pii": row.get("pii_risk_level"),
                "legal_ok": _bool_to_flag(row.get("legal_validation_status")),
                "hash_sha256": row.get("file_hash_sha256"),
            }
        )
    return pd.DataFrame(normalized)


def render_catalog_dashboard() -> None:
    st.header("Carnet de bord des datasets")

    rows = catalog_repo.list_catalog_rows()
    if not rows:
        st.warning("Le carnet de bord est vide. Commencez par ingérer un dataset.", icon="⚠️")
        return

    df = _build_catalog_dataframe(rows)

    colf1, colf2, colf3, colf4 = st.columns(4)
    with colf1:
        search_query = st.text_input("Recherche libre", placeholder="titre, source, sujet, nom standardisé...")
    with colf2:
        state_filter = st.multiselect(
            "État",
            sorted([x for x in df["etat"].dropna().unique().tolist() if x]),
        )
    with colf3:
        source_type_filter = st.multiselect(
            "Type source",
            sorted([x for x in df["type_source"].dropna().unique().tolist() if x]),
        )
    with colf4:
        pii_filter = st.selectbox("PII", ["Tous", "Oui", "Non"], index=0)

    filtered = df.copy()

    if search_query.strip():
        q = search_query.strip().lower()
        filtered = filtered[
            filtered.apply(
                lambda row: q in " ".join(
                    [
                        str(row.get("titre", "")).lower(),
                        str(row.get("topic", "")).lower(),
                        str(row.get("source", "")).lower(),
                        str(row.get("nom_standardise", "")).lower(),
                        str(row.get("hash_sha256", "")).lower(),
                    ]
                ),
                axis=1,
            )
        ]

    if state_filter:
        filtered = filtered[filtered["etat"].isin(state_filter)]

    if source_type_filter:
        filtered = filtered[filtered["type_source"].isin(source_type_filter)]

    if pii_filter != "Tous":
        filtered = filtered[filtered["pii"] == pii_filter]

    total_datasets = filtered["dataset_id"].nunique()
    total_versions = filtered["version_id"].nunique()
    total_pii = (filtered["pii"] == "Oui").sum()
    total_legal_ok = (filtered["legal_ok"] == "Oui").sum()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Datasets", total_datasets)
    k2.metric("Versions", total_versions)
    k3.metric("Versions avec PII", int(total_pii))
    k4.metric("Validation légale OK", int(total_legal_ok))

    st.markdown("### Résultats")
    if filtered.empty:
        st.info("Aucun dataset ne correspond aux filtres actuels.", icon="ℹ️")
        return

    display_cols = [
        "dataset_id",
        "version_id",
        "titre",
        "topic",
        "source",
        "etat",
        "version_label",
        "nom_standardise",
        "date_extraction",
        "lignes",
        "colonnes",
        "pii",
        "risque_pii",
        "legal_ok",
    ]

    st.dataframe(
        filtered[display_cols].sort_values(by=["dataset_id", "version_id"], ascending=[True, False]),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    st.subheader("Inspection rapide")

    selected_version_id = st.selectbox(
        "Choisir une version",
        filtered["version_id"].dropna().tolist(),
        format_func=lambda x: _format_version_label(x, rows),
    )

    selected_row = next((r for r in rows if r.get("version_id") == selected_version_id), None)
    if not selected_row:
        st.warning("Version introuvable.", icon="⚠️")
        return

    left, right = st.columns([1.1, 1.2])

    with left:
        st.markdown("#### Fiche rapide")
        st.json(
            {
                "dataset_id": selected_row.get("dataset_id"),
                "version_id": selected_row.get("version_id"),
                "title": selected_row.get("title"),
                "topic": selected_row.get("topic"),
                "source_name": selected_row.get("source_name"),
                "source_type": selected_row.get("source_type"),
                "processing_state": selected_row.get("processing_state"),
                "version_label": selected_row.get("version_label"),
                "standardized_name": selected_row.get("standardized_name"),
                "extraction_date": selected_row.get("extraction_date"),
                "file_hash_sha256": selected_row.get("file_hash_sha256"),
                "contains_pii": selected_row.get("contains_pii"),
                "pii_risk_level": selected_row.get("pii_risk_level"),
                "legal_validation_status": selected_row.get("legal_validation_status"),
            }
        )

    with right:
        st.markdown("#### Derniers signaux")
        quality_audits = audits_repo.list_quality_audits_by_version_id(selected_version_id)
        integrity_audits = integrity_repo.list_by_version_id(selected_version_id)

        latest_quality = quality_audits[0] if quality_audits else None
        latest_integrity = integrity_audits[0] if integrity_audits else None

        c1, c2 = st.columns(2)
        with c1:
            if latest_quality:
                st.metric("Dernier score qualité", latest_quality.get("quality_score"))
                st.caption(f'Audité le {_fmt_dt(latest_quality.get("audit_timestamp"))}')
            else:
                st.metric("Dernier score qualité", "—")
                st.caption("Aucun audit qualité")

        with c2:
            if latest_integrity:
                st.metric(
                    "Dernière vérif. intégrité",
                    "MATCH" if latest_integrity.get("is_match") else "MISMATCH",
                )
                st.caption(f'Audité le {_fmt_dt(latest_integrity.get("audited_at"))}')
            else:
                st.metric("Dernière vérif. intégrité", "—")
                st.caption("Aucun audit intégrité")

    st.markdown("---")
    st.subheader("Lineage rapide")

    lineage = versions_repo.get_lineage_chain(selected_version_id)
    if not lineage:
        st.caption("Aucune chaîne de lineage disponible.")
    else:
        for node in lineage:
            depth = _safe_num(node.get("depth"), 0)
            indent = "&nbsp;" * 6 * depth
            st.markdown(
                f"{indent}↳ **{node.get('version_label', '—')}** — `{node.get('standardized_name', '—')}`",
                unsafe_allow_html=True,
            )


def _format_version_label(version_id: int, rows: list[dict]) -> str:
    for row in rows:
        if row.get("version_id") == version_id:
            return (
                f'#{row.get("version_id")} · '
                f'{row.get("title", "Sans titre")} · '
                f'{row.get("version_label", "—")} · '
                f'{row.get("standardized_name", "—")}'
            )
    return str(version_id)