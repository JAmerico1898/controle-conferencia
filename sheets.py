"""
Módulo de persistência — Google Sheets (com cache)
Inclui lógica de alocação automática de prédio/quarto/cama.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from config import COLUNAS_PLANILHA, CONTROLE_COLUNAS, PREDIOS, COMBINACOES_OCUPACAO

CACHE_TTL = 30
CONTROLE_SHEET = "_controle"


# ──────────────────────────────────────────────
# Conexão
# ──────────────────────────────────────────────

def _get_gspread_client():
    import gspread
    from google.oauth2.service_account import Credentials
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)


def _get_spreadsheet():
    client = _get_gspread_client()
    sid = st.secrets.get("spreadsheet_id", "")
    if not sid:
        st.error("❌ `spreadsheet_id` não configurado nos Secrets.")
        st.stop()
    try:
        return client.open_by_key(sid)
    except Exception as e:
        st.error(f"❌ Erro ao acessar planilha `{sid}`: {e}")
        st.stop()


# ──────────────────────────────────────────────
# Aba de Controle
# ──────────────────────────────────────────────

def _get_or_create_controle():
    sp = _get_spreadsheet()
    try:
        ws = sp.worksheet(CONTROLE_SHEET)
    except Exception:
        ws = sp.add_worksheet(title=CONTROLE_SHEET, rows=100, cols=10)
        ws.update("A1:G1", [CONTROLE_COLUNAS])
    return ws


@st.cache_data(ttl=CACHE_TTL)
def _carregar_controle_cached():
    ws = _get_or_create_controle()
    return ws.get_all_records()


def carregar_controle():
    data = _carregar_controle_cached()
    if not data:
        return pd.DataFrame(columns=CONTROLE_COLUNAS)
    return pd.DataFrame(data)


def obter_conferencia_ativa():
    df = carregar_controle()
    if df.empty:
        return None
    ativas = df[df["ativa"].astype(str).str.upper() == "SIM"]
    if ativas.empty:
        return None
    return ativas.iloc[0].to_dict()


def abrir_conferencia(mes: int, ano: int, data_inicio: str, data_fim: str, ocupacao: str):
    from config import MESES_CONFERENCIA
    nome_mes = MESES_CONFERENCIA[mes]
    nome_aba = f"{ano}-{mes:02d}-{nome_mes}"

    df_ctrl = carregar_controle()
    ws_ctrl = _get_or_create_controle()
    if not df_ctrl.empty:
        for i, row in df_ctrl.iterrows():
            if str(row["ativa"]).upper() == "SIM":
                ws_ctrl.update_cell(i + 2, 7, "NÃO")  # coluna G = ativa

    nova_linha = [nome_aba, nome_mes, str(ano), data_inicio, data_fim, ocupacao, "SIM"]
    ws_ctrl.append_row(nova_linha)

    sp = _get_spreadsheet()
    try:
        sp.worksheet(nome_aba)
    except Exception:
        ws_new = sp.add_worksheet(title=nome_aba, rows=200, cols=25)
        ws_new.update("A1:T1", [COLUNAS_PLANILHA])

    _invalidar_cache()
    return nome_aba


def fechar_conferencia():
    df_ctrl = carregar_controle()
    ws_ctrl = _get_or_create_controle()
    if not df_ctrl.empty:
        for i, row in df_ctrl.iterrows():
            if str(row["ativa"]).upper() == "SIM":
                ws_ctrl.update_cell(i + 2, 7, "NÃO")
    _invalidar_cache()


def listar_conferencias():
    df = carregar_controle()
    if df.empty:
        return []
    return df["nome_aba"].tolist()


def obter_ocupacao_conferencia(nome_aba: str) -> dict:
    """Retorna mapeamento gênero→prédio para a conferência."""
    df = carregar_controle()
    if df.empty:
        return {}
    row = df[df["nome_aba"] == nome_aba]
    if row.empty:
        return {}
    ocupacao_str = str(row.iloc[0].get("ocupacao", ""))
    for label, mapa in COMBINACOES_OCUPACAO.items():
        if label == ocupacao_str:
            return mapa
    return {}


# ──────────────────────────────────────────────
# Inscrições
# ──────────────────────────────────────────────

def _get_worksheet(nome_aba: str):
    sp = _get_spreadsheet()
    return sp.worksheet(nome_aba)


@st.cache_data(ttl=CACHE_TTL)
def _carregar_inscricoes_cached(nome_aba: str):
    ws = _get_worksheet(nome_aba)
    return ws.get_all_records()


def carregar_inscricoes(nome_aba: str) -> pd.DataFrame:
    data = _carregar_inscricoes_cached(nome_aba)
    if not data:
        return pd.DataFrame(columns=COLUNAS_PLANILHA)
    df = pd.DataFrame(data)
    for col in COLUNAS_PLANILHA:
        if col not in df.columns:
            df[col] = ""
    return df


def carregar_inscricoes_ativas(nome_aba: str) -> pd.DataFrame:
    df = carregar_inscricoes(nome_aba)
    if df.empty:
        return df
    return df[df["status"].astype(str).str.upper() != "CANCELADO"].reset_index(drop=True)


def verificar_nome_duplicado(nome_aba: str, nome: str) -> bool:
    df = carregar_inscricoes_ativas(nome_aba)
    if df.empty:
        return False
    nomes = df["nome"].str.strip().str.upper()
    return nome.strip().upper() in nomes.values


def contar_vagas(nome_aba: str):
    """Retorna dict com vagas por prédio e tipo de cama."""
    df = carregar_inscricoes_ativas(nome_aba)
    resultado = {}
    for predio_nome, cap in PREDIOS.items():
        if predio_nome == "Prédio Extra":
            continue  # Extra é gerido manualmente
        if df.empty:
            alojados = pd.DataFrame()
        else:
            alojados = df[df["alojamento"].astype(str) == predio_nome]
        baixo_oc = len(alojados[alojados["tipo_cama"].astype(str).str.upper() == "BAIXO"]) if not alojados.empty else 0
        cima_oc = len(alojados[alojados["tipo_cama"].astype(str).str.upper() == "CIMA"]) if not alojados.empty else 0
        resultado[predio_nome] = {
            "baixo_ocupado": baixo_oc,
            "cima_ocupado": cima_oc,
            "baixo_disponivel": cap["baixo"] - baixo_oc,
            "cima_disponivel": cap["cima"] - cima_oc,
            "total_ocupado": baixo_oc + cima_oc,
            "total_disponivel": cap["total"] - baixo_oc - cima_oc,
        }
    return resultado


def calcular_quarto_cama(nome_aba: str, predio: str, tipo_cama: str):
    """
    Calcula o próximo quarto e cama disponíveis.
    Retorna (quarto: int, cama: int).
    """
    df = carregar_inscricoes_ativas(nome_aba)
    cap = PREDIOS[predio]

    if df.empty:
        alojados = pd.DataFrame()
    else:
        alojados = df[
            (df["alojamento"].astype(str) == predio) &
            (df["tipo_cama"].astype(str).str.upper() == tipo_cama.upper())
        ]

    ocupados = len(alojados) if not alojados.empty else 0

    if predio == "Prédio Antigo":
        return 1, ocupados + 1

    elif predio == "Prédio Novo":
        camas_por_quarto = cap["camas_por_quarto_baixo"] if tipo_cama.upper() == "BAIXO" else cap["camas_por_quarto_cima"]
        quarto = (ocupados // camas_por_quarto) + 1
        cama = (ocupados % camas_por_quarto) + 1
        return quarto, cama

    elif predio == "Prédio Extra":
        return 1, ocupados + 1

    return 0, 0


def gerar_codigo(nome_aba: str) -> str:
    from config import PREFIXO_MES
    df = carregar_inscricoes(nome_aba)
    partes = nome_aba.split("-")
    ano = partes[0]
    mes = int(partes[1])
    prefixo = PREFIXO_MES.get(mes, "CON")
    seq = len(df) + 1
    return f"{prefixo}{ano}-{seq:03d}"


def salvar_inscricao(nome_aba: str, dados: dict):
    ws = _get_worksheet(nome_aba)
    linha = [str(dados.get(col, "")) for col in COLUNAS_PLANILHA]
    ws.append_row(linha, value_input_option="USER_ENTERED")
    _invalidar_cache()


def cancelar_inscricao(nome_aba: str, nome: str) -> bool:
    ws = _get_worksheet(nome_aba)
    data = ws.get_all_records()
    if not data:
        return False
    for i, row in enumerate(data):
        if (row.get("nome", "").strip().upper() == nome.strip().upper()
                and str(row.get("status", "")).upper() != "CANCELADO"):
            row_num = i + 2
            col_status = COLUNAS_PLANILHA.index("status") + 1
            col_cancel = COLUNAS_PLANILHA.index("data_cancelamento") + 1
            ws.update_cell(row_num, col_status, "Cancelado")
            ws.update_cell(row_num, col_cancel, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            _invalidar_cache()
            return True
    return False


def buscar_inscricao_por_nome(nome_aba: str, nome: str) -> dict | None:
    df = carregar_inscricoes_ativas(nome_aba)
    if df.empty:
        return None
    match = df[df["nome"].str.strip().str.upper() == nome.strip().upper()]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def atualizar_inscricao(nome_aba: str, nome_original: str, dados_atualizados: dict):
    ws = _get_worksheet(nome_aba)
    data = ws.get_all_records()
    for i, row in enumerate(data):
        if row.get("nome", "").strip().upper() == nome_original.strip().upper():
            row_num = i + 2
            linha = [str(dados_atualizados.get(col, row.get(col, ""))) for col in COLUNAS_PLANILHA]
            num_cols = len(COLUNAS_PLANILHA)
            last_col = chr(ord("A") + num_cols - 1) if num_cols <= 26 else "T"
            col_range = f"A{row_num}:{last_col}{row_num}"
            ws.update(col_range, [linha], value_input_option="USER_ENTERED")
            _invalidar_cache()
            return True
    return False


# ──────────────────────────────────────────────
# Cache
# ──────────────────────────────────────────────

def _invalidar_cache():
    _carregar_controle_cached.clear()
    _carregar_inscricoes_cached.clear()
