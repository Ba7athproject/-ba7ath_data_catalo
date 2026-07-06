# ui/dashboard_ingest.py
from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st

from services.ingest_service import IngestService
from services.quality_audit_service import QualityAuditService
from database.repositories.catalog import CatalogRepository
from database.repositories.versions import VersionsRepository


ingest_service = IngestService()
quality_service = QualityAuditService()
catalog_repo = CatalogRepository()
versions_repo = VersionsRepository()


PROCESSING_STATES = ["RAW", "PROCESSING", "CLEAN"]

ACQUISITION_VECTORS = [
    "Scraping automatisé",
    "API officielle",
    "Téléchargement direct / DDL",
    "OSINT Manuel",
    "Fuite / Leak",
    "Autre",
]

PROCESSING_STEPS_OPTIONS = [
    "Nettoyage de base",
    "Réconciliation / Jointure",
    "Fuzzy Matching",
    "Déduplication",
    "Normalisation des colonnes",
    "Traitement par LLM",
]


def _save_uploaded_file(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name


def _build_ai_details(prompt_text: str, model_name: str) -> dict:
    payload = {}
    if model_name.strip():
        payload["model"] = model_name.strip()
    if prompt_text.strip():
        payload["prompt"] = prompt_text.strip()
    return payload


def _render_audit_result(audit_result: dict) -> None:
    st.subheader("Résultat de l’audit qualité")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Score global", audit_result.get("quality_score"))
    c2.metric("Complétude", audit_result.get("completeness_score"))
    c3.metric("Unicité", audit_result.get("uniqueness_score"))
    c4.metric("Cohérence", audit_result.get("consistency_score"))
    c5.metric("Sensibilité", audit_result.get("sensitivity_score"))

    c6, c7, c8 = st.columns(3)
    c6.metric("Lignes", audit_result.get("row_count"))
    c7.metric("Colonnes", audit_result.get("column_count"))
    c8.metric("Null ratio", audit_result.get("null_ratio"))

    with st.expander("Détails audit qualité", expanded=False):
        st.json(audit_result)


def render_ingest_tab() -> None:
    st.header("Nouvelle entrée / nouvelle version")

    uploaded_file = st.file_uploader(
        "Téléverser le fichier pour analyse et scellement",
        type=["csv", "tsv", "xlsx", "xls", "json"],
        key="uploader_ingest_v2",
    )

    parsed = None
    if uploaded_file is not None:
        parsed = ingest_service.parse_filename(uploaded_file.name)

    default_date = datetime.today().date()
    default_source = ""
    default_topic = ""
    default_state = "RAW"

    if parsed:
        try:
            default_date = datetime.fromisoformat(parsed["extraction_date"]).date()
        except Exception:
            pass
        default_source = parsed.get("source_name", "") or ""
        default_topic = parsed.get("topic", "") or ""
        default_state = parsed.get("processing_state", "RAW") or "RAW"

    rows = catalog_repo.list_catalog_rows()
    version_options = []
    for row in rows:
        if row.get("version_id"):
            version_options.append(row)

    with st.form("ingest_form_v2", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Nomenclature dynamique")

            is_derived = st.checkbox("Ce fichier est une modification / évolution d’un dataset existant")
            parent_version_id = None

            if is_derived and version_options:
                selected_parent = st.selectbox(
                    "Sélectionner la version parent / origine",
                    version_options,
                    format_func=lambda x: f'#{x["version_id"]} · {x.get("standardized_name", "—")}',
                )
                parent_version_id = selected_parent["version_id"]

            extraction_date = st.date_input("Date d’extraction", value=default_date)
            title = st.text_input("Titre dataset", placeholder="Ex. Marchés publics 2024")
            source_name = st.text_input("Source / Producteur", value=default_source)
            topic = st.text_input("Sujet / Thématique", value=default_topic)
            processing_state = st.selectbox(
                "État",
                PROCESSING_STATES,
                index=PROCESSING_STATES.index(default_state) if default_state in PROCESSING_STATES else 0,
            )

        with col2:
            st.markdown("### Méthodologie & cadre légal")

            source_url = st.text_input("URL source", placeholder="https://...")
            source_type = st.selectbox(
                "Type de source",
                ["official", "scraped", "leak", "archive", "third_party", "unknown"],
                index=5,
            )
            acquisition_vector = st.selectbox("Vecteur d’acquisition", ACQUISITION_VECTORS)
            processing_steps = st.multiselect("Traitements appliqués", PROCESSING_STEPS_OPTIONS)
            model_name = st.text_input("Modèle IA", placeholder="Ex. GPT-4.1 / Mistral / Llama")
            prompt_llm = st.text_area(
                "Détails IA / Prompt",
                height=120,
            )
            legal_validation_status = st.checkbox("J’atteste la conformité légale et éthique de la collecte")
            contains_pii = st.checkbox("Contient des données personnelles / PII")
            pii_risk_level = st.selectbox("Niveau de risque PII", ["none", "low", "medium", "high"], index=1)

        description = st.text_area(
            "Description / contexte",
            placeholder="Contexte, limites connues, méthode de collecte, dictionnaire, réserves éditoriales...",
            height=110,
        )

        created_by = st.text_input("Créé par", placeholder="Ex. Moez")
        collected_by = st.text_input("Collecté par", placeholder="Ex. newsroom-bot")
        audit_notes = st.text_area("Notes audit", placeholder="Commentaires facultatifs", height=90)

        extraction_date_str = extraction_date.strftime("%Y-%m-%d")
        proposed_name = ingest_service.build_standardized_name(
            extraction_date=extraction_date_str,
            source_name=source_name or "INCONNUE",
            topic=topic or "SANS-NOM",
            processing_state=processing_state,
            version_label="vX",
        )
        st.info(f"Identifiant standardisé proposé : {proposed_name}")

        submit = st.form_submit_button("Valider, ingérer et auditer")

    if not submit:
        return

    if uploaded_file is None:
        st.error("Veuillez charger un fichier avant de lancer l’ingestion.", icon="❌")
        return

    if not source_name.strip() or not topic.strip() or not title.strip():
        st.error("Les champs Titre, Source et Sujet sont obligatoires.", icon="❌")
        return

    if not legal_validation_status:
        st.error("La validation de conformité légale est obligatoire.", icon="❌")
        return

    temp_path = None
    try:
        with st.spinner("Sauvegarde temporaire du fichier..."):
            temp_path = _save_uploaded_file(uploaded_file)

        ai_details = _build_ai_details(prompt_llm, model_name)

        with st.spinner("Ingestion, profilage et scellement..."):
            ingest_result = ingest_service.ingest_file(
                file_path=temp_path,
                title=title.strip(),
                topic=topic.strip(),
                source_name=source_name.strip(),
                source_url=source_url.strip() or None,
                source_type=source_type,
                acquisition_vector=acquisition_vector,
                pii_risk_level=pii_risk_level,
                description=description.strip() or None,
                created_by=created_by.strip() or None,
                collected_by=collected_by.strip() or None,
                processing_state=processing_state,
                parent_version_id=parent_version_id,
                legal_validation_status=legal_validation_status,
                contains_pii=contains_pii,
                processing_steps=processing_steps,
                ai_details=ai_details,
                extraction_date=extraction_date_str,
            )

        with st.spinner("Audit qualité automatique..."):
            audit_result = quality_service.run_and_persist_audit(
                dataset_id=ingest_result["dataset"]["id"],
                version_id=ingest_result["version"]["id"],
                audited_by=created_by.strip() or None,
                compared_to_version_id=parent_version_id,
                notes=audit_notes.strip() or None,
            )

        st.session_state["last_ingest_result"] = ingest_result
        st.session_state["last_quality_audit_result"] = audit_result

        st.success("Fiche valide et ajoutée avec succès au carnet de bord.", icon="✅")

    except Exception as exc:
        st.exception(exc)
        return

    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass

    ingest_result = st.session_state["last_ingest_result"]
    st.markdown("### Résultat de l’ingestion")
    st.json(
        {
            "dataset": ingest_result["dataset"],
            "version": ingest_result["version"],
            "profiling": ingest_result["profiling"],
            "profile_id": ingest_result["profile_id"],
            "schema_snapshot_id": ingest_result["schema_snapshot_id"],
        }
    )

    if "last_quality_audit_result" in st.session_state:
        _render_audit_result(st.session_state["last_quality_audit_result"])