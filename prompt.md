# PROMPT — Aplicativo de Gestão de Conferências "O Novo Sol"

---

## CONTEXTO

O centro de conferências **"O Novo Sol"**, localizado em Rio Bonito-RJ, pertence à Escola Espiritual da Rosacruz Áurea e realiza conferências mensais para seus alunos. O centro possui capacidade para alojar até **100 pessoas**, distribuídas em dois alojamentos com beliches:

| Alojamento | Camas de Baixo | Camas de Cima | Total |
|---|---|---|---|
| Feminino | 26 | 24 | 50 |
| Masculino | 25 | 25 | 50 |

**Importante:** O alojamento no centro NÃO é obrigatório para participar da conferência. Há hotéis na região e muitos alunos os utilizam. Portanto, a falta de vagas nos alojamentos não impede a inscrição do aluno.

As conferências ocorrem nos seguintes meses: **fevereiro, março, abril, maio, junho, agosto, setembro, outubro, novembro e dezembro** (não há conferência em janeiro e julho).

---

## ARQUITETURA TÉCNICA

- **Framework**: Streamlit
- **Deploy**: Streamlit Community Cloud
- **Persistência de dados**: Google Sheets (uma planilha por conferência, ex: "2025-03-Março", "2025-04-Abril", etc.)
- **Autenticação da área restrita**: `st.secrets` com 5 usuários gestores (login e senha)
- **Credenciais do Google Sheets**: armazenadas em `st.secrets` (service account JSON)
- **Histórico**: O sistema mantém todas as planilhas de conferências anteriores para consulta. Apenas uma conferência pode estar ativa (aberta para inscrições) por vez.

---

## ÁREA PÚBLICA (padrão do aplicativo)

A área pública é a tela inicial do aplicativo. Ela só fica disponível para inscrições quando o gestor define um período de abertura na área restrita. Fora desse período, a tela pública exibe uma mensagem informativa: *"As inscrições para a próxima conferência ainda não foram abertas. Aguarde comunicação da coordenação."*

### Painel de Vagas (visível sempre que inscrições estiverem abertas)

Exibir no topo da página um resumo atualizado em tempo real:

```
📅 Conferência de [Mês/Ano] — Inscrições abertas até [data fim]
🛏️ Alojamento Feminino: X baixo / Y cima disponíveis
🛏️ Alojamento Masculino: X baixo / Y cima disponíveis
👥 Total de inscritos: N
```

### Formulário de Inscrição

Os campos devem seguir a ordem abaixo, com os fluxos condicionais indicados:

1. **Nome completo** (texto livre, obrigatório) — Chave única. Se já existir inscrição com o mesmo nome, rejeitar com mensagem: *"Já existe uma inscrição registrada com este nome. Caso precise fazer alterações, utilize a opção de cancelamento abaixo."*
2. **Gênero** (seletor: Masculino / Feminino)
3. **Cidade** (texto livre)
4. **Estado** (seletor com os 26 estados + DF)
5. **Discipulado** (seletor: 1º Aspecto / 2º Aspecto / 3º Aspecto / 4º Aspecto / Graal / Escola Interior)
6. **Precisa de alojamento no centro de conferências?** (Sim / Não)

#### Se "Precisa de alojamento" = SIM:

7. **Precisa de cama de baixo?** (Sim / Não)
   - O sistema verifica a disponibilidade conforme o gênero do aluno e o tipo de cama solicitado.
   - **Lógica de verificação:**
     - Se o tipo solicitado (baixo ou cima) estiver esgotado, informar ao aluno com mensagem contextualizada. Exemplo: *"Não há mais camas de baixo disponíveis no alojamento masculino. Ainda restam X camas de cima. Deseja uma cama de cima?"*
     - Se ambos os tipos estiverem esgotados: *"Não há mais vagas no alojamento [feminino/masculino]. Você pode se inscrever sem alojamento e buscar hospedagem na região."*
     - O aluno pode aceitar a alternativa oferecida ou prosseguir sem alojamento.

8. **Data de chegada** (seletor: Sexta à tarde / Sexta à noite / Sábado de manhã)

9. **Refeições** (múltipla seleção com validação cruzada):
   - As opções de refeição disponíveis dependem da data de chegada:
     - **Sexta à tarde**: Jantar de Sexta ✅ | Almoço de Sábado ✅ | Jantar de Sábado ✅ | Lanche de Domingo ✅
     - **Sexta à noite**: Jantar de Sexta ✅ | Almoço de Sábado ✅ | Jantar de Sábado ✅ | Lanche de Domingo ✅
     - **Sábado de manhã**: Almoço de Sábado ✅ | Jantar de Sábado ✅ | Lanche de Domingo ✅
   - **Café da manhã de domingo**: adicionado automaticamente e obrigatoriamente para todos os alunos alojados (não aparece como opção — é incluído no resumo final com a nota: *"O café da manhã de domingo está incluído para todos os alunos alojados."*)

#### Se "Precisa de alojamento" = NÃO:

- Pular perguntas 7 e 8.
- **Refeições** (múltipla seleção): Almoço de Sábado / Jantar de Sábado / Lanche de Domingo
- **Não incluir** café da manhã de domingo.

10. **Email** (texto livre, obrigatório — para referência, sem envio automático)

### Tela de Confirmação

Após submissão bem-sucedida, exibir:

- ✅ Mensagem de confirmação: *"Inscrição realizada com sucesso!"*
- **Código de inscrição**: gerar código único (ex: `MAR2025-042`)
- **Resumo completo** de todos os dados informados
- Se alojado, incluir: tipo de cama atribuída + nota sobre café da manhã de domingo
- Botão para **imprimir/salvar** o resumo (via `st.download_button` gerando um PDF ou texto)

### Cancelamento de Inscrição

Na área pública, incluir uma seção (pode ser em aba ou expander) para cancelamento:

- O aluno informa seu **nome completo** exatamente como cadastrado.
- O sistema localiza a inscrição e exibe o resumo para confirmação.
- Após confirmação do cancelamento:
  - O registro é marcado como **cancelado** na planilha (não excluído, para manter histórico).
  - As vagas de alojamento são liberadas e os contadores atualizados.
  - Mensagem: *"Sua inscrição para a Conferência de [Mês] foi cancelada com sucesso."*

---

## ÁREA RESTRITA

Acesso via botão discreto no canto da página (ex: ícone ⚙️ ou link "Área Administrativa"). A autenticação utiliza login e senha armazenados em `st.secrets`. São 5 usuários gestores.

### Gestão da Conferência

1. **Abrir inscrições para uma conferência:**
   - Selecionar o mês da conferência (fevereiro a dezembro, exceto janeiro e julho)
   - O ano é preenchido automaticamente (ano corrente, ou o gestor pode ajustar)
   - Definir **data de início** e **data de fim** das inscrições
   - Ao abrir, o sistema cria a planilha correspondente no Google Sheets (se não existir)
   - Apenas uma conferência pode estar ativa por vez

2. **Fechar inscrições manualmente:**
   - Botão para encerrar as inscrições antes da data fim, se necessário

3. **Consultar conferências anteriores:**
   - Seletor com lista de todas as conferências passadas
   - Ao selecionar, carrega os dashboards e a lista de inscritos daquela conferência

### Gestão de Inscrições

- **Lista completa de inscritos** da conferência ativa (tabela interativa com filtros)
- **Editar inscrição**: o gestor pode alterar qualquer campo de um inscrito
- **Cancelar inscrição**: o gestor pode cancelar a inscrição de um aluno (liberando vagas)
- **Exportar dados**: botão para download em CSV e/ou Excel com todos os inscritos

### Dashboards (conferência ativa ou selecionada)

Todos os dashboards devem atualizar em tempo real (a cada carregamento da página):

1. **Resumo Geral**
   - Total de inscritos (ativos, excluindo cancelados)
   - Total de alojados vs. não alojados
   - Vagas restantes por alojamento e tipo de cama (gráfico de barras: capacidade vs. ocupado)

2. **Inscritos por Gênero**
   - Gráfico de pizza ou barras: masculino vs. feminino

3. **Inscritos por Discipulado**
   - Gráfico de barras: quantidade por nível de discipulado

4. **Inscritos por Cidade/Estado**
   - Tabela agrupada ou gráfico de barras horizontal com os estados mais representados
   - Detalhamento por cidade disponível via expansão

5. **Contagem de Refeições**
   - Tabela com o total de cada refeição solicitada (fundamental para logística de cozinha):
     - Jantar de Sexta: N
     - Café da manhã de Sábado: N (se aplicável)
     - Almoço de Sábado: N
     - Jantar de Sábado: N
     - Café da manhã de Domingo: N (= total de alojados)
     - Lanche de Domingo: N

6. **Lista Exportável**
   - Tabela completa com todos os campos, filtrável e ordenável
   - Botões de exportação: CSV e Excel

---

## REGRAS IMPORTANTES

- O nome é a chave única de inscrição. Não permitir duplicatas (considerar normalização: remover espaços extras, capitalizar).
- Inscrições canceladas devem permanecer na planilha com status "Cancelado" — nunca excluir registros.
- O café da manhã de domingo é **exclusivo e obrigatório** para alojados.
- A validação cruzada de refeições por horário de chegada deve ser feita no frontend (Streamlit) para melhor UX — não permitir que o aluno marque refeições anteriores à sua chegada.
- O painel de vagas na área pública deve refletir a situação real (descontando cancelamentos).
- O sistema deve tratar erros de conexão com o Google Sheets de forma elegante, exibindo mensagem amigável ao usuário.

---

## ESTRUTURA SUGERIDA DE ABAS/NAVEGAÇÃO

### Área Pública
- **Inscrição** (padrão)
- **Cancelamento**

### Área Restrita
- **Gestão da Conferência** (abrir/fechar/histórico)
- **Inscrições** (lista, editar, cancelar, exportar)
- **Dashboards**

---

## DADOS NO GOOGLE SHEETS

Cada conferência deve ter sua própria aba (sheet) dentro de uma mesma planilha Google Sheets, nomeada no formato: `AAAA-MM-Mês` (ex: `2025-03-Março`).

Colunas sugeridas para cada aba:
| Coluna | Descrição |
|---|---|
| codigo_inscricao | Código único gerado (ex: MAR2025-001) |
| nome | Nome completo |
| genero | Masculino / Feminino |
| cidade | Cidade de residência |
| estado | UF |
| discipulado | Nível do discipulado |
| alojamento | Sim / Não |
| tipo_cama | Baixo / Cima / N/A |
| data_chegada | Sexta à tarde / Sexta à noite / Sábado de manhã |
| jantar_sexta | Sim / Não |
| almoco_sabado | Sim / Não |
| jantar_sabado | Sim / Não |
| cafe_domingo | Sim / Não |
| lanche_domingo | Sim / Não |
| email | Email do aluno |
| data_inscricao | Timestamp da inscrição |
| status | Ativo / Cancelado |
| data_cancelamento | Timestamp do cancelamento (se aplicável) |