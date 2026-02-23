"""
<img src="{rosacruz_url}" style="height: 1.5em; vertical-align: middle; margin-right: 0.3em;"> Gestão de Conferências — Centro "O NOVO SOL"
Escola Espiritual da Rosacruz Áurea

Aplicativo principal Streamlit.
"""

import streamlit as st
rosacruz_url = "https://raw.githubusercontent.com/JAmerico1898/controle-conferencia/3603d1046888c033126d727cf9df5e7a3ab50720/rosacruz.png"

#https://github.com/JAmerico1898/controle-conferencia/blob/3603d1046888c033126d727cf9df5e7a3ab50720/rosacruz.png

# ──────────────────────────────────────────────
# Configuração da página
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Conferências O NOVO SOL",
    page_icon=rosacruz_url,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# CSS customizado
# ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #e94560;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #e94560;
    }

    /* Esconder menu hamburger e footer do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────
# Navegação
# ──────────────────────────────────────────────

def main():
    # Inicializar estado
    if "modo" not in st.session_state:
        st.session_state["modo"] = "publico"

    # Sidebar mínima com botão de acesso admin
    with st.sidebar:
        st.markdown(
                    f"""
                    <h3 style="margin-bottom: 0;">
                        <img src="{rosacruz_url}" width="26" style="vertical-align: -5px; margin-right: 8px;">
                        <span style="color: #DAA520;">O Novo Sol</span>
                    </h3>
                    """,
                    unsafe_allow_html=True
                )
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

    # Renderizar área correspondente
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
