"""
Configurações e constantes do aplicativo de Gestão de Conferências "O Novo Sol"
"""

# ──────────────────────────────────────────────
# Capacidade dos alojamentos por PRÉDIO
# ──────────────────────────────────────────────
PREDIOS = {
    "Prédio Antigo": {"baixo": 25, "cima": 25, "total": 50, "quartos": 1, "camas_por_quarto_baixo": 25, "camas_por_quarto_cima": 25},
    "Prédio Novo":   {"baixo": 24, "cima": 24, "total": 48, "quartos": 4, "camas_por_quarto_baixo": 6, "camas_por_quarto_cima": 6},
    "Prédio Extra":  {"baixo": 2,  "cima": 0,  "total": 2,  "quartos": 1, "camas_por_quarto_baixo": 2, "camas_por_quarto_cima": 0},
}

# Combinações de ocupação
COMBINACOES_OCUPACAO = {
    "Homens → Prédio Antigo / Mulheres → Prédio Novo": {
        "Masculino": "Prédio Antigo",
        "Feminino": "Prédio Novo",
    },
    "Homens → Prédio Novo / Mulheres → Prédio Antigo": {
        "Masculino": "Prédio Novo",
        "Feminino": "Prédio Antigo",
    },
}

# Meses com conferência (sem janeiro e julho)
MESES_CONFERENCIA = {
    2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
    8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

# Prefixos para código de inscrição
PREFIXO_MES = {
    2: "FEV", 3: "MAR", 4: "ABR", 5: "MAI", 6: "JUN",
    8: "AGO", 9: "SET", 10: "OUT", 11: "NOV", 12: "DEZ",
}

# Estados brasileiros
ESTADOS_BR = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA",
    "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN",
    "RO", "RR", "RS", "SC", "SE", "SP", "TO",
]

# Níveis de discipulado
DISCIPULADOS = [
    "1º Aspecto", "2º Aspecto", "3º Aspecto", "4º Aspecto",
    "Graal", "Escola Interior",
]

# Opções de data de chegada
DATAS_CHEGADA = ["Sexta à tarde", "Sexta à noite", "Sábado de manhã"]

# Refeições disponíveis por data de chegada
REFEICOES_POR_CHEGADA = {
    "Sexta à tarde": ["Jantar de Sexta", "Almoço de Sábado", "Jantar de Sábado", "Lanche de Domingo"],
    "Sexta à noite": ["Jantar de Sexta", "Almoço de Sábado", "Jantar de Sábado", "Lanche de Domingo"],
    "Sábado de manhã": ["Almoço de Sábado", "Jantar de Sábado", "Lanche de Domingo"],
}

# Refeições para não-alojados
REFEICOES_NAO_ALOJADO = ["Almoço de Sábado", "Jantar de Sábado", "Lanche de Domingo"]

# Colunas da planilha (ATUALIZADO com quarto e cama)
COLUNAS_PLANILHA = [
    "codigo_inscricao", "nome", "genero", "cidade", "estado",
    "discipulado", "alojamento", "quarto", "cama", "tipo_cama",
    "data_chegada", "jantar_sexta", "almoco_sabado", "jantar_sabado",
    "cafe_domingo", "lanche_domingo", "email",
    "data_inscricao", "status", "data_cancelamento",
]

# Colunas da aba de controle (ATUALIZADO com ocupação)
CONTROLE_COLUNAS = [
    "nome_aba", "mes", "ano", "data_inicio", "data_fim", "ocupacao", "ativa"
]
