# app.py
from __future__ import annotations

# pyrefly: ignore [missing-import]
import streamlit as st

from database.connection import init_db
from ui.dashboard_home import render_home
from ui.dashboard_ingest import render_ingest_tab
from ui.dashboard_catalog import render_catalog_dashboard
from ui.dashboard_dataset_detail import render_dataset_dashboard


st.set_page_config(
    page_title="Ba7ath Data Catalog Audit",
    page_icon="🧪",
    layout="wide",
)

init_db()

st.title("Ba7ath DATA Catalog")
st.markdown(
    "Outil de traçabilité, de gestion des versions, de contrôle qualité "
    "et de certification de l’intégrité des preuves."
)

with st.sidebar:
    try:
        st.image("ui/logo.png", use_column_width=True)
    except FileNotFoundError:
        pass
    st.header("Navigation")
    page = st.radio(
        "Aller vers",
        [
            "Accueil",
            "Ingestion / Versioning",
            "Carnet de bord",
            "Détail dataset",
        ],
        index=0,
    )

if page == "Accueil":
    render_home()
elif page == "Ingestion / Versioning":
    render_ingest_tab()
elif page == "Carnet de bord":
    render_catalog_dashboard()
elif page == "Détail dataset":
    render_dataset_dashboard()