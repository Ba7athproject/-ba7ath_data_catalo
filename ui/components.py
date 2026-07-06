import streamlit as st

def render_badge(label: str, color: str = "blue"):
    score_map = {
        "green": "#16a34a",
        "orange": "#ea580c",
        "red": "#dc2626",
        "blue": "#2563eb",
        "gray": "#6b7280",
    }

    bg_map = {
        "green": "#dcfce7",
        "orange": "#ffedd5",
        "red": "#fee2e2",
        "blue": "#dbeafe",
        "gray": "#f3f4f6",
    }

    text_color = score_map.get(color, "#2563eb")
    bg_color = bg_map.get(color, "#dbeafe")

    st.markdown(
        f"""
        <div style="
            display:inline-block;
            padding:0.35rem 0.7rem;
            border-radius:999px;
            font-weight:600;
            color:{text_color};
            background:{bg_color};
            border:1px solid {text_color}22;
        ">
            {label}
        </div>
        """,
        unsafe_allow_html=True,
    )
