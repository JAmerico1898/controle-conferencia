"""
Área Pública — Inscrição e Cancelamento
"""

import streamlit as st
from datetime import datetime
from config import (
    ESTADOS_BR, DISCIPULADOS, DATAS_CHEGADA,
    REFEICOES_POR_CHEGADA, REFEICOES_NAO_ALOJADO, PREDIOS,
)
from sheets import (
    obter_conferencia_ativa, carregar_inscricoes_ativas,
    verificar_nome_duplicado, contar_vagas, gerar_codigo,
    salvar_inscricao, cancelar_inscricao, buscar_inscricao_por_nome,
    obter_ocupacao_conferencia, calcular_quarto_cama,
)

rosacruz_url = "https://raw.githubusercontent.com/JAmerico1898/controle-conferencia/43dd0c98bfddc62c7803a9c9c7523d0ad3303871/rosacruz.png"


def exibir_area_publica():
    conf = obter_conferencia_ativa()

    if conf is None:
        _exibir_inscricoes_fechadas()
        return

    hoje = datetime.now().strftime("%Y-%m-%d")
    if hoje < conf.get("data_inicio", "") or hoje > conf.get("data_fim", ""):
        _exibir_inscricoes_fechadas()
        return

    nome_aba = conf["nome_aba"]
    mes_nome = conf["mes"]
    ano = conf["ano"]
    data_fim = conf["data_fim"]

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
             padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
             border-left: 4px solid #e94560;">
            <h2 style="color: #e94560; margin: 0;">
                <img src="{rosacruz_url}" style="height: 1.5em; vertical-align: middle; margin-right: 0.3em;">
                Conferência de {mes_nome}/{ano}
            </h2>
            <p style="color: #555; margin: 0.5rem 0 0 0;">
                Inscrições abertas até {_formatar_data(data_fim)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _exibir_painel_vagas(nome_aba)

    tab_inscricao, tab_cancelamento = st.tabs(["📝 Inscrição", "❌ Cancelamento"])

    with tab_inscricao:
        _formulario_inscricao(nome_aba, mes_nome, ano)

    with tab_cancelamento:
        _formulario_cancelamento(nome_aba, mes_nome)


def _exibir_inscricoes_fechadas():
    st.markdown(
        f"""
        <div style="text-align: center; padding: 4rem 2rem;">
            <img src="{rosacruz_url}" style="height: 4em;">
            <h2 style="color: #333;">Escola Espiritual da Rosacruz Áurea</h2>
            <h3 style="color: #555;">Centro de Conferências <span style="color: #DAA520;">O NOVO SOL</span></h3>
            <hr style="margin: 2rem auto; width: 50%; border-color: #ddd;">
            <p style="font-size: 1.1rem; color: #666;">
                As inscrições para a próxima conferência ainda não foram abertas.<br>
                Aguarde comunicação da coordenação.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _exibir_painel_vagas(nome_aba: str):
    try:
        vagas = contar_vagas(nome_aba)
        df = carregar_inscricoes_ativas(nome_aba)
        total_inscritos = len(df)
        ocupacao = obter_ocupacao_conferencia(nome_aba)
    except Exception:
        st.warning("Não foi possível carregar as vagas. Tente novamente.")
        return

    col1, col2, col3 = st.columns(3)

    # Determinar qual prédio é de quem
    predio_masc = ocupacao.get("Masculino", "")
    predio_fem = ocupacao.get("Feminino", "")

    with col1:
        if predio_masc in vagas:
            vm = vagas[predio_masc]
            st.metric(f"🛏️ Masculino ({predio_masc})", f"{vm['total_disponivel']} vagas")
            st.caption(f"Baixo: {vm['baixo_disponivel']} | Cima: {vm['cima_disponivel']}")

    with col2:
        if predio_fem in vagas:
            vf = vagas[predio_fem]
            st.metric(f"🛏️ Feminino ({predio_fem})", f"{vf['total_disponivel']} vagas")
            st.caption(f"Baixo: {vf['baixo_disponivel']} | Cima: {vf['cima_disponivel']}")

    with col3:
        st.metric("👥 Total de Inscritos", total_inscritos)

    st.divider()


def _formulario_inscricao(nome_aba: str, mes_nome: str, ano: str):
    if st.session_state.get("inscricao_confirmada"):
        _exibir_confirmacao()
        if st.button("📝 Nova Inscrição", type="primary"):
            st.session_state.pop("inscricao_confirmada", None)
            st.session_state.pop("dados_confirmacao", None)
            st.rerun()
        return

    st.subheader("Formulário de Inscrição")

    nome = st.text_input("Nome completo *", key="pub_nome")
    genero = st.selectbox("Gênero *", ["", "Masculino", "Feminino"], key="pub_genero")
    cidade = st.text_input("Cidade *", key="pub_cidade")
    estado = st.selectbox("Estado *", [""] + ESTADOS_BR, key="pub_estado")
    discipulado = st.selectbox("Discipulado *", [""] + DISCIPULADOS, key="pub_discipulado")

    precisa_alojamento = st.radio(
        "Precisa de alojamento no centro de conferências? *",
        ["Sim", "Não"], key="pub_alojamento", horizontal=True,
    )

    tipo_cama = "N/A"
    alojamento_predio = "Não"
    quarto_num = ""
    cama_num = ""
    data_chegada = ""
    refeicoes_selecionadas = []
    cafe_domingo = False

    if precisa_alojamento == "Sim":
        ocupacao = obter_ocupacao_conferencia(nome_aba)
        vagas = contar_vagas(nome_aba)
        predio_destino = ocupacao.get(genero, "") if genero else ""

        precisa_baixo = st.radio(
            "Precisa de cama de baixo? *",
            ["Sim", "Não"], key="pub_cama_baixo", horizontal=True,
        )

        if genero and predio_destino and predio_destino in vagas:
            vg = vagas[predio_destino]
            tipo_solicitado = "baixo" if precisa_baixo == "Sim" else "cima"
            tipo_alternativo = "cima" if precisa_baixo == "Sim" else "baixo"

            if vg[f"{tipo_solicitado}_disponivel"] <= 0:
                alt_disp = vg[f"{tipo_alternativo}_disponivel"]
                if alt_disp > 0:
                    st.warning(
                        f"Não há mais camas de {tipo_solicitado} disponíveis no {predio_destino}. "
                        f"Ainda restam **{alt_disp}** camas de {tipo_alternativo}."
                    )
                    aceitar = st.radio(
                        f"Deseja uma cama de {tipo_alternativo}?",
                        ["Sim", "Não, prosseguir sem alojamento"],
                        key="pub_aceitar_alt", horizontal=True,
                    )
                    if aceitar.startswith("Sim"):
                        tipo_cama = tipo_alternativo.capitalize()
                        alojamento_predio = predio_destino
                    else:
                        alojamento_predio = "Não"
                        precisa_alojamento = "Não"
                        st.info("Você será inscrito sem alojamento.")
                else:
                    st.error(
                        f"Não há mais vagas no {predio_destino}. "
                        f"Você pode se inscrever sem alojamento."
                    )
                    alojamento_predio = "Não"
                    precisa_alojamento = "Não"
            else:
                tipo_cama = "Baixo" if precisa_baixo == "Sim" else "Cima"
                alojamento_predio = predio_destino

        data_chegada = st.selectbox("Data de chegada *", [""] + DATAS_CHEGADA, key="pub_chegada")

        if data_chegada:
            refeicoes_disponiveis = REFEICOES_POR_CHEGADA[data_chegada]
            refeicoes_selecionadas = st.multiselect(
                "Refeições desejadas", refeicoes_disponiveis,
                default=refeicoes_disponiveis, key="pub_refeicoes",
            )

        if alojamento_predio != "Não":
            cafe_domingo = True
            st.info("☕ O café da manhã de domingo está incluído para todos os alunos alojados.")
    else:
        refeicoes_selecionadas = st.multiselect(
            "Refeições desejadas", REFEICOES_NAO_ALOJADO,
            default=REFEICOES_NAO_ALOJADO, key="pub_refeicoes_na",
        )

    email = st.text_input("Email para referência *", key="pub_email")
    st.divider()

    if st.button("✅ Confirmar Inscrição", type="primary", use_container_width=True):
        erros = []
        if not nome.strip(): erros.append("Nome é obrigatório.")
        if not genero: erros.append("Gênero é obrigatório.")
        if not cidade.strip(): erros.append("Cidade é obrigatória.")
        if not estado: erros.append("Estado é obrigatório.")
        if not discipulado: erros.append("Discipulado é obrigatório.")
        if not email.strip(): erros.append("Email é obrigatório.")
        if alojamento_predio != "Não" and not data_chegada:
            erros.append("Data de chegada é obrigatória para alojados.")

        if erros:
            for e in erros:
                st.error(e)
            return

        nome_normalizado = " ".join(nome.strip().split()).title()

        if verificar_nome_duplicado(nome_aba, nome_normalizado):
            st.error("Já existe inscrição com este nome. Use a aba de **Cancelamento** para alterações.")
            return

        # Calcular quarto e cama
        if alojamento_predio not in ["Não", ""]:
            quarto_num, cama_num = calcular_quarto_cama(nome_aba, alojamento_predio, tipo_cama)
        else:
            quarto_num, cama_num = "", ""

        codigo = gerar_codigo(nome_aba)

        dados = {
            "codigo_inscricao": codigo,
            "nome": nome_normalizado,
            "genero": genero,
            "cidade": cidade.strip().title(),
            "estado": estado,
            "discipulado": discipulado,
            "alojamento": alojamento_predio if alojamento_predio != "Não" else "Não",
            "quarto": str(quarto_num) if quarto_num else "N/A",
            "cama": str(cama_num) if cama_num else "N/A",
            "tipo_cama": tipo_cama if alojamento_predio != "Não" else "N/A",
            "data_chegada": data_chegada if alojamento_predio != "Não" else "N/A",
            "jantar_sexta": "Sim" if "Jantar de Sexta" in refeicoes_selecionadas else "Não",
            "almoco_sabado": "Sim" if "Almoço de Sábado" in refeicoes_selecionadas else "Não",
            "jantar_sabado": "Sim" if "Jantar de Sábado" in refeicoes_selecionadas else "Não",
            "cafe_domingo": "Sim" if cafe_domingo else "Não",
            "lanche_domingo": "Sim" if "Lanche de Domingo" in refeicoes_selecionadas else "Não",
            "email": email.strip(),
            "data_inscricao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Ativo",
            "data_cancelamento": "",
        }

        try:
            salvar_inscricao(nome_aba, dados)
            st.session_state["inscricao_confirmada"] = True
            st.session_state["dados_confirmacao"] = dados
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar inscrição: {e}")


def _exibir_confirmacao():
    dados = st.session_state.get("dados_confirmacao", {})
    st.success("✅ Inscrição realizada com sucesso!")

    st.markdown(
        f"""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px;
             border: 1px solid #e94560; margin: 1rem 0;">
            <h3 style="color: #e94560; margin-top: 0;">
                Código: {dados.get('codigo_inscricao', '')}
            </h3>
        </div>
        """, unsafe_allow_html=True,
    )

    st.markdown("### Resumo da Inscrição")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Nome:** {dados.get('nome', '')}")
        st.markdown(f"**Gênero:** {dados.get('genero', '')}")
        st.markdown(f"**Cidade/Estado:** {dados.get('cidade', '')}/{dados.get('estado', '')}")
        st.markdown(f"**Discipulado:** {dados.get('discipulado', '')}")
        st.markdown(f"**Email:** {dados.get('email', '')}")

    with col2:
        aloj = dados.get("alojamento", "Não")
        st.markdown(f"**Alojamento:** {aloj}")
        if aloj != "Não":
            quarto = dados.get("quarto", "")
            cama = dados.get("cama", "")
            tipo = dados.get("tipo_cama", "")
            if aloj == "Prédio Novo":
                st.markdown(f"**Quarto {quarto}, Cama de {tipo.lower()} {cama}**")
            else:
                st.markdown(f"**Cama de {tipo.lower()} {cama}**")
            st.markdown(f"**Chegada:** {dados.get('data_chegada', '')}")

        refeicoes = []
        if dados.get("jantar_sexta") == "Sim": refeicoes.append("Jantar de Sexta")
        if dados.get("almoco_sabado") == "Sim": refeicoes.append("Almoço de Sábado")
        if dados.get("jantar_sabado") == "Sim": refeicoes.append("Jantar de Sábado")
        if dados.get("cafe_domingo") == "Sim": refeicoes.append("☕ Café da manhã de Domingo")
        if dados.get("lanche_domingo") == "Sim": refeicoes.append("Lanche de Domingo")
        st.markdown(f"**Refeições:** {', '.join(refeicoes) if refeicoes else 'Nenhuma'}")

    if dados.get("cafe_domingo") == "Sim":
        st.info("☕ O café da manhã de domingo está incluído automaticamente para alunos alojados.")

    st.caption("⚠️ O gestor poderá alterar os parâmetros de inscrição para melhor acomodar os alunos.")

    resumo_txt = _gerar_resumo_texto(dados)
    st.download_button(
        "📄 Baixar comprovante", data=resumo_txt,
        file_name=f"inscricao_{dados.get('codigo_inscricao', 'conf')}.txt",
        mime="text/plain",
    )


def _gerar_resumo_texto(dados: dict) -> str:
    linhas = [
        "=" * 50,
        "COMPROVANTE DE INSCRIÇÃO",
        'Centro de Conferências O NOVO SOL',
        "Escola Espiritual da Rosacruz Áurea",
        "=" * 50, "",
        f"Código: {dados.get('codigo_inscricao', '')}",
        f"Data da inscrição: {dados.get('data_inscricao', '')}", "",
        f"Nome: {dados.get('nome', '')}",
        f"Gênero: {dados.get('genero', '')}",
        f"Cidade/Estado: {dados.get('cidade', '')}/{dados.get('estado', '')}",
        f"Discipulado: {dados.get('discipulado', '')}",
        f"Email: {dados.get('email', '')}", "",
        f"Alojamento: {dados.get('alojamento', '')}",
    ]
    if dados.get("alojamento") not in ["Não", ""]:
        linhas.append(f"Quarto: {dados.get('quarto', '')}")
        linhas.append(f"Cama: {dados.get('tipo_cama', '').lower()} {dados.get('cama', '')}")
        linhas.append(f"Data de chegada: {dados.get('data_chegada', '')}")
    linhas.append("")
    linhas.append("Refeições:")
    if dados.get("jantar_sexta") == "Sim": linhas.append("  • Jantar de Sexta")
    if dados.get("almoco_sabado") == "Sim": linhas.append("  • Almoço de Sábado")
    if dados.get("jantar_sabado") == "Sim": linhas.append("  • Jantar de Sábado")
    if dados.get("cafe_domingo") == "Sim": linhas.append("  • Café da manhã de Domingo")
    if dados.get("lanche_domingo") == "Sim": linhas.append("  • Lanche de Domingo")
    linhas.append("")
    linhas.append("Obs: O gestor poderá alterar os parâmetros de inscrição")
    linhas.append("para melhor acomodar os alunos.")
    linhas.extend(["", "=" * 50])
    return "\n".join(linhas)


def _formulario_cancelamento(nome_aba: str, mes_nome: str):
    st.subheader("Cancelamento de Inscrição")
    st.caption("Informe seu nome completo exatamente como cadastrado.")

    nome_cancel = st.text_input("Nome completo", key="pub_cancel_nome")

    if st.button("🔍 Buscar Inscrição", key="btn_buscar_cancel"):
        if not nome_cancel.strip():
            st.error("Informe seu nome.")
            return
        inscricao = buscar_inscricao_por_nome(nome_aba, nome_cancel)
        if inscricao is None:
            st.warning("Nenhuma inscrição ativa encontrada com este nome.")
            return
        st.session_state["inscricao_para_cancelar"] = inscricao

    if st.session_state.get("inscricao_para_cancelar"):
        insc = st.session_state["inscricao_para_cancelar"]
        st.markdown(f"**Código:** {insc.get('codigo_inscricao', '')}")
        st.markdown(f"**Nome:** {insc.get('nome', '')}")
        st.markdown(f"**Alojamento:** {insc.get('alojamento', '')}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚠️ Confirmar Cancelamento", type="primary"):
                try:
                    cancelar_inscricao(nome_aba, insc["nome"])
                    st.success(f"Inscrição para a Conferência de {mes_nome} cancelada com sucesso.")
                    st.session_state.pop("inscricao_para_cancelar", None)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cancelar: {e}")
        with col2:
            if st.button("Voltar"):
                st.session_state.pop("inscricao_para_cancelar", None)
                st.rerun()


def _formatar_data(data_str: str) -> str:
    try:
        dt = datetime.strptime(data_str, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return data_str
