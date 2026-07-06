# ui/dashboard_home.py
from __future__ import annotations

import streamlit as st

from database.repositories.catalog import CatalogRepository
from database.repositories.audits import AuditsRepository
from database.repositories.integrity_audits import IntegrityAuditsRepository


catalog_repo = CatalogRepository()
audits_repo = AuditsRepository()
integrity_repo = IntegrityAuditsRepository()


def render_home() -> None:
    st.header("Vue d’ensemble")

    rows = catalog_repo.list_catalog_rows()
    dataset_count = len(set(r["dataset_id"] for r in rows)) if rows else 0
    version_count = len(set(r["version_id"] for r in rows if r.get("version_id"))) if rows else 0

    all_quality = audits_repo.list_recent_quality_audits(limit=10)
    all_integrity = integrity_repo.list_recent(limit=10)

    match_count = sum(1 for a in all_integrity if a.get("is_match"))
    mismatch_count = sum(1 for a in all_integrity if not a.get("is_match"))

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Datasets", dataset_count)
    k2.metric("Versions", version_count)
    k3.metric("Audits qualité récents", len(all_quality))
    k4.metric("Audits intégrité récents", len(all_integrity))

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Couverture fonctionnelle")
        st.markdown(
            """
- Ingestion et scellement cryptographique
- Versioning parent / enfant
- Profilage et audit qualité
- Carnet de bord consultable
- Audit d’intégrité anti-tampering
            """
        )

    with c2:
        st.markdown("### Signaux intégrité")
        st.markdown(
            f"""
- MATCH récents : **{match_count}**
- MISMATCH récents : **{mismatch_count}**
            """
        )

    st.markdown("---")
    st.markdown("### Orientation newsroom")
    st.info(
        "Le catalogue sert à documenter la provenance, la qualité, les transformations "
        "et l’intégrité des datasets utilisés dans une enquête."
    )