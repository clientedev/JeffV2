# 🚂 Deploy Completo no Railway

Este guia explica como fazer o deploy completo da aplicação no Railway com PostgreSQL.

## ✅ O Que Acontece Automaticamente no Deploy

Quando você fizer deploy no Railway:

1. **Tabelas são criadas automaticamente** - O sistema verifica e cria as 27 tabelas necessárias
2. **Dados são importados automaticamente** - Na primeira inicialização, todos os dados das planilhas são importados:
   - 3.003 contatos
   - 993 empresas
   - 20 consultores
   - 2.940 registros linha tecnologia
   - 266 registros linha educacional
   - 4.967 alocações de cronograma
   - **383 empresas no pipeline kanban**
   - **817 empresas na prospecção**

3. **Dados são preservados** - Uma vez importados, os dados NÃO são sobrescritos em reinicializações

## 🚀 Deploy no Railway - Passo a Passo Completo

### 1. Preparar Repositório GitHub

1. **Crie um repositório no GitHub** (se ainda não tiver)
2. **Faça push do código para o GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Deploy inicial Railway"
   git branch -M main
   git remote add origin https://github.com/seu-usuario/seu-repo.git
   git push -u origin main
   ```

### 2. Criar Projeto no Railway

1. Acesse [Railway.app](https://railway.app)
2. Faça login com GitHub
3. Clique em **"New Project"**
4. Selecione **"Deploy from GitHub repo"**
5. Escolha seu repositório
6. Railway irá detectar automaticamente que é uma aplicação Python/FastAPI

### 3. Adicionar PostgreSQL ao Projeto

1. No mesmo projeto Railway, clique em **"+ New"**
2. Selecione **"Database"** → **"Add PostgreSQL"**
3. Railway criará automaticamente o banco PostgreSQL
4. A variável `DATABASE_URL` será configurada automaticamente

### 4. Configurar Variáveis de Ambiente

No Railway, vá em seu serviço web → **Variables** e adicione:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
ADMIN_EMAIL=admin@sistema.com
ADMIN_PASSWORD=admin123
```

**Observações Importantes:**
- Railway fornece automaticamente a variável `$PORT` - **NÃO configure manualmente**
- Railway conecta automaticamente `${{Postgres.DATABASE_URL}}` ao seu banco PostgreSQL
- A aplicação irá escutar na porta fornecida pelo Railway automaticamente

### 5. Configurar Domínio Público

1. No Railway, vá em seu serviço web
2. Clique na aba **"Settings"**
3. Vá em **"Networking"** → **"Generate Domain"**
4. Railway criará um domínio público como: `seu-app.up.railway.app`

### 6. Deploy Automático

Railway fará deploy automaticamente quando você:
- Fizer push para o branch main
- Modificar variáveis de ambiente
- Clicar em "Deploy" manualmente

O sistema irá:
- ✅ Instalar todas as dependências do `requirements.txt`
- ✅ Iniciar a aplicação com uvicorn
- ✅ Conectar ao banco PostgreSQL automaticamente
- ✅ Criar todas as 27 tabelas no primeiro startup
- ✅ Importar todos os dados das planilhas Excel
- ✅ Criar usuário admin padrão

## 📁 Arquivos de Configuração Railway

O projeto já possui os seguintes arquivos configurados:

### `railway.json`
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### `Procfile`
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### `runtime.txt`
```
python-3.11
```

### `requirements.txt`
Contém todas as dependências necessárias do projeto.

## 🔍 Verificação do Deploy

### Verificar Logs no Railway

1. No Railway, acesse seu serviço web
2. Clique em **"Deployments"**
3. Selecione o deploy mais recente
4. Clique em **"View Logs"**

Você deve ver nos logs:

```
INFO:     Started server process
INFO:     Waiting for application startup.
======================================================================
🔍 VERIFICAÇÃO DE ESTRUTURA DO BANCO DE DADOS
======================================================================
📊 Tabelas existentes no banco: 0
⚠️  Tabelas faltantes detectadas: 27
   ⚙️  Criando tabela: usuarios
   ⚙️  Criando tabela: empresas
   ...
✅ Tabelas criadas com sucesso!
INFO:app.seed_data:Importando contatos...
INFO:app.seed_data:3003 contatos importados com sucesso!
...
INFO:     Application startup complete.
```

### Acessar Aplicação

1. Abra o domínio gerado: `https://seu-app.up.railway.app`
2. Você verá a tela de login
3. Use as credenciais padrão:
   - **Email:** admin@sistema.com
   - **Senha:** admin123

### Verificar Banco de Dados no Railway

1. No Railway, acesse o serviço PostgreSQL
2. Clique em **"Data"** para ver as tabelas
3. Ou use **"Connect"** para conectar via SQL client

Após conectar, verifique:

```bash
# Ver tabelas criadas
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

# Ver quantidade de registros
SELECT 
  (SELECT COUNT(*) FROM empresas) as empresas,
  (SELECT COUNT(*) FROM consultores) as consultores,
  (SELECT COUNT(*) FROM company_pipeline) as pipeline,
  (SELECT COUNT(*) FROM prospeccao) as prospeccao;
```

## 🛡️ Segurança dos Dados

- ✅ **Sem perda de dados**: O sistema nunca remove dados existentes
- ✅ **Importação única**: Os dados são importados apenas uma vez
- ✅ **Verificação automática**: O sistema verifica se tabelas/dados já existem antes de criar
- ✅ **Rollback automático**: Em caso de erro, as transações são revertidas

## 📊 Estrutura de Tabelas

O sistema cria automaticamente 27 tabelas:

1. **usuarios** - Usuários do sistema
2. **empresas** - Empresas cadastradas
3. **consultores** - Consultores
4. **propostas** - Propostas comerciais
5. **cronogramas** - Cronogramas de projetos
6. **tarefas** - Tarefas dos cronogramas
7. **contratos** - Contratos assinados
8. **feriados** - Feriados
9. **alocacoes_cronograma** - Alocações de consultores
10. **contatos** - Contatos de empresas
11. **linha_tecnologia** - Programas linha tecnologia
12. **linha_educacional** - Programas linha educacional
13. **prospeccao** - Prospecção de novos clientes
14. **followups** - Follow-ups de prospecção
15. **carteira_grm** - Carteira GRM
16. **pesquisas_satisfacao** - Pesquisas de satisfação
17. **solucoes** - Catálogo de soluções
18. **stages** - Estágios do pipeline
19. **company_pipeline** - Empresas no pipeline kanban
20. **company_stage_history** - Histórico de movimentação no pipeline
21. **notes** - Notas sobre empresas
22. **attachments** - Anexos
23. **activities** - Log de atividades
24. **email_contatos** - Contatos de email
25. **campanhas_email** - Campanhas de email marketing
26. **campanha_destinatarios** - Destinatários das campanhas
27. **anexos_email** - Anexos de emails

## ⚡ Migrações Futuras

O sistema possui um mecanismo de migração seguro que:

- Adiciona novas colunas automaticamente
- Nunca remove colunas existentes
- Nunca remove tabelas existentes
- Preserva todos os dados

## 🆘 Troubleshooting Railway

### ❌ Erro: "Error creating build plan with Railpack"

**Causa:** Railway não detectou os arquivos de configuração corretamente.

**Solução:**
1. Certifique-se que os arquivos existem na raiz do projeto:
   - `requirements.txt`
   - `railway.json`
   - `Procfile`
   - `runtime.txt`
2. Faça commit e push dos arquivos:
   ```bash
   git add requirements.txt railway.json Procfile runtime.txt
   git commit -m "Adicionar configuração Railway"
   git push origin main
   ```
3. No Railway, clique em **"Redeploy"**

### ❌ Deploy falha com erro de dependências

**Solução:**
1. Verifique se `requirements.txt` está correto
2. Certifique-se que `runtime.txt` especifica Python 3.11
3. Verifique logs de build no Railway

### ❌ Aplicação não inicia - Port Error

**Causa:** A aplicação não está usando a variável `$PORT` do Railway.

**Solução:**
1. Verifique que `railway.json` tem: `--port $PORT`
2. Railway fornece a variável `$PORT` automaticamente - **NÃO configure manualmente**
3. Redeploy após correção

### ❌ Dados não aparecem após deploy

**Solução:** Verifique os logs do servidor para confirmar a importação:
```
INFO:app.seed_data:Importando dados para pipeline...
INFO:app.seed_data:Importando dados para prospecção...
```

Se não aparecer, verifique:
1. PostgreSQL está conectado corretamente
2. Variável `DATABASE_URL` está configurada: `${{Postgres.DATABASE_URL}}`
3. Logs de erro durante importação

### ❌ Erro 502 Bad Gateway

**Causa:** Aplicação não está respondendo na porta correta.

**Solução:**
1. Verifique que uvicorn está iniciando: `INFO: Uvicorn running on`
2. Verifique que está usando `0.0.0.0` como host
3. Verifique que está usando `$PORT` do Railway
4. Aguarde alguns minutos - Railway pode demorar para propagar

### ❌ Banco de dados vazio após deploy

**Causa:** Importação de dados falhou ou ainda não foi executada.

**Solução:**
1. Verifique logs completos no Railway → View Logs
2. Procure por erros na seção de startup:
   ```
   ✅ Tabelas criadas com sucesso!
   INFO:app.seed_data:3003 contatos importados com sucesso!
   ```
3. Se não encontrar, faça redeploy manual
4. Verifique se os arquivos Excel estão no repositório em `attached_assets/`

### ❌ Tabelas não criadas

**Solução:** O sistema cria automaticamente no startup. Verifique os logs:
```
✅ Tabelas criadas com sucesso!
```

Se não aparecer:
1. Verifique conexão com PostgreSQL
2. Confirme que `DATABASE_URL` está configurada
3. Verifique permissões do banco de dados

## 📋 Checklist Pré-Deploy

Antes de fazer deploy no Railway, confirme:

- [ ] Repositório GitHub criado e código commitado
- [ ] Arquivo `requirements.txt` na raiz do projeto
- [ ] Arquivo `railway.json` na raiz do projeto
- [ ] Arquivo `Procfile` na raiz do projeto
- [ ] Arquivo `runtime.txt` especificando Python 3.11
- [ ] Arquivos Excel em `attached_assets/` commitados no repositório
- [ ] PostgreSQL adicionado ao projeto Railway
- [ ] Variável `DATABASE_URL=${{Postgres.DATABASE_URL}}` configurada
- [ ] Domínio público gerado no Railway

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs completos no Railway Dashboard
2. Confirme que a variável `DATABASE_URL` está configurada corretamente
3. Verifique se todos os arquivos de configuração foram commitados
4. Faça redeploy manual se necessário
5. Aguarde 2-3 minutos após deploy para aplicação inicializar completamente

---

**Sistema de Relacionamento com a Indústria v1.03**
