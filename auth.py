"""
Módulo de autenticação para a área restrita.
"""

import streamlit as st


def autenticar():
    if st.session_state.get("autenticado", False):
        return True

    st.subheader("🔐 Área Administrativa")
    st.caption("Acesso restrito aos gestores do sistema.")

    with st.form("login_form"):
        login = st.text_input("Login")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

    if submit:
        gestores = st.secrets.get("gestores", {}).get("users", [])
        for g in gestores:
            if g["login"] == login and g["senha"] == senha:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = login
                st.rerun()
        st.error("Login ou senha inválidos.")

    return False


def logout():
    st.session_state["autenticado"] = False
    st.session_state.pop("usuario", None)
    st.rerun()
