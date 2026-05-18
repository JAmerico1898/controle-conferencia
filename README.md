# 🌹 Gestão de Conferências — Centro "O Novo Sol"

Aplicativo Streamlit para gerenciar inscrições nas conferências mensais da Escola Espiritual da Rosacruz Áurea.

---

## 📁 Estrutura do Projeto

```
conferencia/
├── app.py                 # Aplicativo principal (ponto de entrada)
├── config.py              # Constantes e configurações
├── sheets.py              # Persistência no Google Sheets (Service Account)
├── auth.py                # Autenticação da área restrita
├── area_publica.py        # Inscrição e cancelamento
├── area_restrita.py       # Gestão, inscrições e dashboards
├── requirements.txt       # Dependências Python
├── secrets_example.toml   # Exemplo de configuração de secrets
└── README.md              # Este arquivo
```

---

## 🚀 Guia de Deploy — Passo a Passo

### Passo 1: Criar a Service Account no Google Cloud

1. Acesse [Google Cloud Console](https://console.cloud.google.com).
2. Crie um projeto (ou use um existente).
3. Ative as APIs:
   - **Google Sheets API** (busque em "APIs & Services > Library")
   - **Google Drive API** (idem)
4. Vá em **APIs & Services > Credentials > Create Credentials > Service Account**.
5. Dê um nome (ex: "conferencias-bot") e clique em **Create and Continue**.
6. Pule a etapa de permissões (clique em **Continue** e depois **Done**).
7. Na lista de Service Accounts, clique na que você criou.
8. Vá na aba **Keys > Add Key > Create new key > JSON**.
9. O arquivo JSON será baixado automaticamente. **Guarde-o com segurança.**

> ⚠️ **Você NÃO precisa compartilhar nenhuma planilha manualmente.**
> O app cria a planilha automaticamente usando a Service Account
> e compartilha com seu email.

### Passo 2: Subir o código no GitHub

1. Crie um repositório no GitHub.
2. Faça upload dos arquivos:
   - `app.py`, `config.py`, `sheets.py`, `auth.py`
   - `area_publica.py`, `area_restrita.py`
   - `requirements.txt`
3. ⚠️ **NÃO suba** o arquivo JSON da Service Account nem o `secrets_example.toml`

### Passo 3: Deploy no Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io).
2. Clique em **New app** e conecte ao repositório GitHub.
3. Configure **Main file path**: `app.py`
4. Vá em **Advanced Settings > Secrets** e cole:

   ```toml
   # Deixe vazio na PRIMEIRA vez — o app cria a planilha automaticamente
   spreadsheet_id = ""

   # Seu email para receber acesso à planilha
   email_proprietario = "seu.email@gmail.com"

   # Cole o conteúdo INTEIRO do arquivo JSON entre aspas simples
   gcp_service_account = '{"type": "service_account", ...TODO O CONTEÚDO DO JSON...}'

   [gestores]
   users = [
       {login = "gestor1", senha = "sua_senha"},
       {login = "gestor2", senha = "sua_senha"},
       {login = "gestor3", senha = "sua_senha"},
       {login = "gestor4", senha = "sua_senha"},
       {login = "gestor5", senha = "sua_senha"},
   ]
   ```

5. Clique em **Deploy**.

### Passo 4: Primeira Execução

1. Na primeira vez que o app rodar, ele vai:
   - Criar a planilha "Conferências O Novo Sol" automaticamente
   - Compartilhar com seu email (você receberá um convite no Gmail)
   - Exibir o **ID da planilha** na tela
2. Copie o ID exibido.
3. Vá em **Settings > Secrets** do app no Streamlit Cloud.
4. Atualize `spreadsheet_id = "ID_COPIADO"`.
5. Reinicie o app (clique em **Reboot app**).
6. Pronto! A partir de agora o app usa essa planilha.

---

## 🔧 Como Funciona

### Área Pública (padrão)
- Painel de vagas em tempo real
- Formulário de inscrição com validações
- Cancelamento de inscrição pelo aluno
- Comprovante para download

### Área Restrita (gestores)
- Abrir/fechar conferências
- Gerenciar inscrições (editar, cancelar, exportar)
- Dashboards: gênero, discipulado, estado, refeições, alojamento
- Histórico de todas as conferências

---

## ⚠️ Notas Importantes

- **Apenas uma conferência pode estar ativa por vez.**
- O nome do aluno é a chave única — duplicatas são rejeitadas.
- Inscrições canceladas ficam no histórico (nunca são excluídas).
- O café da manhã de domingo é incluído automaticamente para alojados.
- A aba `_controle` no Google Sheets gerencia os metadados — **não a edite manualmente**.
- A planilha pertence à Service Account. Você acessa como Editor via compartilhamento automático.
