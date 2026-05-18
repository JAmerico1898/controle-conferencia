# Gestão de Conferências — Centro "O NOVO SOL"

Aplicativo Streamlit para gerenciar inscrições de conferências da Escola Espiritual da Rosacruz Áurea — Centro "O Novo Sol". Permite ao público realizar/cancelar inscrições enquanto há uma conferência ativa, e a gestores administrarem conferências, inscritos e relatórios. A persistência é feita inteiramente em uma planilha Google Sheets (uma aba por conferência + uma aba `_controle`).

---

## 1. Arquitetura geral

```
┌────────────────────────────────────────────────────┐
│                     app.py                         │
│  (entry point Streamlit · navegação público/admin) │
└──────────────┬───────────────────────┬─────────────┘
               │                       │
               ▼                       ▼
       area_publica.py         auth.py  →  area_restrita.py
       (inscrição/cancel.)     (login)     (gestão/dashboards)
               │                              │
               └──────────────┬───────────────┘
                              ▼
                          sheets.py
              (gspread + cache + alocação de cama)
                              │
                              ▼
                       Google Sheets
              ( aba _controle + abas por conferência )
                              ▲
                              │
                          config.py
                (constantes: prédios, meses, colunas…)
```

### Fluxo de execução
1. `app.py` configura a página, a sidebar e decide entre **Área Pública** e **Área Administrativa** com base em `st.session_state["modo"]`.
2. A **Área Pública** consulta `sheets.obter_conferencia_ativa()`. Se houver conferência ativa dentro do período, exibe os formulários de inscrição/cancelamento; caso contrário, exibe a tela de inscrições fechadas.
3. A **Área Administrativa** exige autenticação (`auth.autenticar()`) e expõe três abas: gestão da conferência, gestão de inscrições e dashboards.
4. Toda leitura/escrita de dados passa por `sheets.py`, que aplica caching (`@st.cache_data(ttl=30)`) e invalidação manual após escritas.

### Modelo de dados (Google Sheets)
- **Aba `_controle`** — uma linha por conferência criada. Colunas (`CONTROLE_COLUNAS`):
  `nome_aba, mes, ano, data_inicio, data_fim, ocupacao, ativa`. Apenas uma conferência tem `ativa = SIM` por vez.
- **Aba por conferência** — nome no formato `AAAA-MM-MesPorExtenso` (ex: `2026-04-Abril`). Colunas (`COLUNAS_PLANILHA`): código de inscrição, dados pessoais, alojamento (prédio/quarto/cama/tipo_cama), data de chegada, refeições, email e status (`Ativo` ou `Cancelado`).

---

## 2. Módulos

### `app.py` — Entry point
- Configura `st.set_page_config` (título, ícone Rosacruz, layout *wide*, sidebar colapsada).
- Injeta CSS customizado (cor `#e94560` em métricas/tabs; esconde menu e footer do Streamlit).
- Mantém `st.session_state["modo"]` em `"publico"` ou `"admin"` e renderiza a área correspondente. Importa `area_publica`/`area_restrita` *lazy*, dentro de cada branch.

### `config.py` — Constantes do domínio
Concentra as regras de negócio estáticas:
- **`PREDIOS`** — capacidade de cada prédio: `Prédio Antigo` (50 camas, 1 quarto, 25 baixo + 25 cima), `Prédio Novo` (48 camas em 4 quartos, 6+6 por quarto), `Prédio Extra` (2 camas, gerido manualmente).
- **`COMBINACOES_OCUPACAO`** — mapeamentos gênero→prédio (ex: "Homens → Antigo / Mulheres → Novo"). Escolhido na abertura da conferência.
- **`MESES_CONFERENCIA`** / **`PREFIXO_MES`** — meses elegíveis (exclui janeiro e julho) e prefixos de código (FEV, MAR, ABR…).
- **`ESTADOS_BR`**, **`DISCIPULADOS`** — listas para selectboxes.
- **`DATAS_CHEGADA`** e **`REFEICOES_POR_CHEGADA`** — refeições disponíveis dependem do horário de chegada (sexta tarde/noite x sábado manhã). `REFEICOES_NAO_ALOJADO` para quem não usa alojamento.
- **`COLUNAS_PLANILHA`** / **`CONTROLE_COLUNAS`** — esquemas das duas abas.

### `auth.py` — Autenticação simples
- `autenticar()` — formulário de login que compara contra a lista `st.secrets["gestores"]["users"]` (lista de `{login, senha}`). Em sucesso, grava `autenticado=True` e `usuario` em `session_state`. Retorna `True/False` e é usado como gate da área restrita.
- `logout()` — limpa o estado de autenticação e força `st.rerun()`.

> Segurança: senhas em texto plano nos secrets. Apropriado apenas para um grupo pequeno de gestores confiáveis. Trocar por hash/IdP se a base crescer.

### `sheets.py` — Persistência e regras de alocação
Camada única que fala com o Google Sheets via `gspread` + `google-oauth2`. Cache TTL de 30s para reduzir chamadas à API; invalidado manualmente por `_invalidar_cache()` após qualquer escrita.

**Conexão**
- `_get_gspread_client()` — autentica com a service account em `st.secrets["gcp_service_account"]` (JSON serializado).
- `_get_spreadsheet()` — abre a planilha por `spreadsheet_id`.

**Aba de controle**
- `_get_or_create_controle()` — garante que `_controle` existe (cria se faltar).
- `carregar_controle()` / `obter_conferencia_ativa()` — lê tudo / filtra a linha ativa.
- `abrir_conferencia(mes, ano, data_inicio, data_fim, ocupacao)` — desativa qualquer conferência ativa, anexa nova linha em `_controle` e cria a aba da conferência com cabeçalho.
- `fechar_conferencia()` — apenas marca a ativa como `NÃO`.
- `obter_ocupacao_conferencia(nome_aba)` — devolve o dict gênero→prédio.

**Inscrições**
- `carregar_inscricoes` / `carregar_inscricoes_ativas` — filtra `status != CANCELADO`.
- `verificar_nome_duplicado` — case-insensitive contra inscrições ativas.
- `contar_vagas(nome_aba)` — devolve por prédio: ocupação e vagas remanescentes em camas baixo/cima/total. Ignora `Prédio Extra` (manual).
- `calcular_quarto_cama(nome_aba, predio, tipo_cama)` — alocação automática:
  - Antigo / Extra: quarto = 1, cama sequencial.
  - Novo: distribui em 4 quartos, `quarto = ocupados // 6 + 1`, `cama = ocupados % 6 + 1` (separadamente para baixo/cima).
- `gerar_codigo` — `<PREFIXO_MES><ano>-<seq:03d>` (ex: `ABR2026-001`).
- `salvar_inscricao` / `cancelar_inscricao` / `buscar_inscricao_por_nome` / `atualizar_inscricao` — CRUD por nome (chave funcional).

### `area_publica.py` — Inscrição e cancelamento

`exibir_area_publica()` é o ponto de entrada. Lógica:
1. Sem conferência ativa **ou** fora da janela `data_inicio..data_fim`: tela "inscrições fechadas".
2. Caso contrário: cabeçalho com mês/ano + painel de vagas + duas abas (Inscrição / Cancelamento).

**Painel de vagas (`_exibir_painel_vagas`)** — mostra três métricas: vagas masculinas, vagas femininas e total de inscritos, derivando o prédio de cada gênero a partir da ocupação configurada.

**Formulário de inscrição (`_formulario_inscricao`)**
- Coleta: nome, gênero, cidade/estado, discipulado, alojamento (Sim/Não), preferência baixo/cima, data de chegada, refeições, email.
- Lógica de fallback de cama: se a preferência (baixo/cima) está esgotada, oferece o tipo alternativo; se ambos esgotados, oferece inscrição sem alojamento.
- Refeições mostradas dependem da data de chegada. Café de domingo é incluído automaticamente para alojados.
- Validações: campos obrigatórios + nome único. Em sucesso: calcula quarto/cama, gera código, persiste e exibe `_exibir_confirmacao`.

**Cancelamento (`_formulario_cancelamento`)** — busca a inscrição por nome, exibe os dados e chama `cancelar_inscricao` (marca status = `Cancelado` e grava timestamp).

### `area_restrita.py` — Gestão administrativa
Três abas:

**Gestão da Conferência (`_gestao_conferencia`)**
- Status da conferência ativa, com botão para fechar.
- Formulário para abrir nova: mês (de `MESES_CONFERENCIA`), datas de início/fim de inscrições, e combinação de ocupação. Ano é derivado da data de início. Bloqueia abertura se já houver uma ativa ou se as datas forem inconsistentes.
- Histórico — `dataframe` de `_controle` formatado em `DD/MM/YYYY`.

**Gestão de Inscrições (`_gestao_inscricoes`)**
- Seleciona conferência (qualquer uma do histórico, com a ativa em destaque).
- Lista inscritos ativos (com colunas de alojamento/quarto/cama/tipo_cama).
- Exporta CSV e Excel (via `openpyxl`).
- **Relatórios DOCX por prédio** (`_gerar_relatorios_predios`) — usa `python-docx`:
  - Antigo: tabela Nome + Tipo de Cama + Nº Cama.
  - Novo: tabela Nome + Quarto + Tipo de Cama + Nº Cama.
  - Extra: tabela só com Nome.
- Cancelar inscrição existente.
- Editar inscrição: permite mover entre prédios (incluindo `Prédio Extra` para realocação manual), trocar tipo de cama, quarto, cama, e demais dados.

**Dashboards (`_dashboards`)**
- Cartões: total / alojados / não alojados.
- Barras de ocupação (baixo + cima) por prédio principal, rotuladas com o gênero alocado.
- Gráficos de barras por gênero, discipulado, estado (com detalhamento por cidade num expander).
- Contagem de refeições (tabela + gráfico) usando `jantar_sexta`, `almoco_sabado`, `jantar_sabado`, `cafe_domingo`, `lanche_domingo`.

**Utilidades**
- `_selecionar_conferencia` — selectbox uniforme (ativa em destaque).
- `_fmt_data` — `YYYY-MM-DD` → `DD/MM/YYYY`.

---

## 3. Configuração e secrets

Arquivo `.streamlit/secrets.toml` (modelo em `secrets_example.toml`) deve conter:

```toml
spreadsheet_id = "<id da planilha do Google>"

# JSON da service account, serializado como string
gcp_service_account = """{ ... }"""

[gestores]
users = [
  { login = "admin", senha = "..." },
]
```

A planilha precisa ser compartilhada com o e-mail da service account (papel Editor). O arquivo `controle-conferencia-37831b339410.json` no repositório é a chave da service account — em produção deve ficar **fora** do repositório.

## 4. Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 5. Ciclo de vida de uma conferência

1. Admin abre conferência → `_controle` ganha linha `ativa=SIM` e a aba `AAAA-MM-Mes` é criada.
2. Público se inscreve → linhas anexadas; alocação automática de prédio/quarto/cama/tipo_cama.
3. Admin acompanha vagas, cancela, edita, exporta e baixa relatórios DOCX.
4. Admin fecha → `ativa=NÃO`. Os dados continuam acessíveis pela aba histórica.

## 6. Pontos de extensão / observações

- **Cache TTL de 30s** (`sheets.CACHE_TTL`): pode atrasar alterações concorrentes; ajustar conforme volume.
- **Concorrência** — duas inscrições simultâneas podem receber o mesmo quarto/cama (não há lock no Sheets). Para volumes maiores, considerar uma transação/lock externo.
- **Senhas em texto plano** — substituir por hash + IdP em uma evolução.
- **Prédio Extra** é gerido manualmente (não entra em `contar_vagas`); a movimentação ocorre via edição administrativa.
- **Coluna de status** usa string (`Ativo` / `Cancelado`); comparações são case-insensitive em `sheets.py`.
