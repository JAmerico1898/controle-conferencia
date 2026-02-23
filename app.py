"""
🌹 Gestão de Conferências — Centro "O Novo Sol"
Escola Espiritual da Rosacruz Áurea
"""

import streamlit as st

st.set_page_config(
    page_title="Conferências O Novo Sol",
    page_icon="🌹",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS
st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #e94560;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #e94560;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    if "modo" not in st.session_state:
        st.session_state["modo"] = "publico"

    with st.sidebar:
        st.markdown('### 🌹 <span style="color: #DAA520;">O Novo Sol</span>', unsafe_allow_html=True)
        st.markdown('<span style="color: #000000;">Centro de Conferências</span>', unsafe_allow_html=True)
        st.divider()

        if st.session_state["modo"] == "publico":
            if st.button("⚙️ Área Administrativa", use_container_width=True):
                st.session_state["modo"] = "admin"
                st.rerun()
        else:
            if st.button("🏠 Voltar à Área Pública", use_container_width=True):
                st.session_state["modo"] = "publico"
                st.session_state.pop("autenticado", None)
                st.rerun()

    if st.session_state["modo"] == "publico":
        from area_publica import exibir_area_publica
        exibir_area_publica()
    elif st.session_state["modo"] == "admin":
        from auth import autenticar
        if autenticar():
            from area_restrita import exibir_area_restrita
            exibir_area_restrita()


if __name__ == "__main__":
    main()
