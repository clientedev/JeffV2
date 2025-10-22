# Sistema de Relacionamento com a Indústria 1.03

Sistema web completo de gerenciamento de relacionamento com empresas, desenvolvido em FastAPI + PostgreSQL.

## 📊 Estado Atual do Sistema

### ✅ Sistema Totalmente Funcional
- FastAPI rodando na porta 5000
- PostgreSQL configurado e populado
- 27 tabelas criadas automaticamente
- Dados importados e permanentes

### 📈 Dados no Sistema

- **993 empresas** cadastradas
- **20 consultores** ativos
- **3.003 contatos** de empresas
- **2.940 registros** de linha tecnologia
- **266 registros** de linha educacional
- **4.967 alocações** de cronograma
- **925 empresas** no pipeline kanban (NOVO!)
- **817 empresas** na prospecção (NOVO!)

### 🔐 Acesso ao Sistema

**Credenciais padrão:**
- Email: `admin@sistema.com`
- Senha: `admin123`

## 🎯 Funcionalidades Principais

### 1. Dashboard
- Visão geral de propostas, contratos e receita
- Gráficos de produtividade de consultores
- Análise de propostas por status

### 2. Gestão de Empresas
- Cadastro completo de empresas
- Histórico de relacionamento
- Vinculação com propostas e contratos

### 3. Gestão de Consultores
- Perfil de consultores
- Produtividade e alocação
- Histórico de projetos

### 4. Pipeline Kanban (NOVO!)
- Visualização em quadro Kanban
- 7 estágios: Prospecção → Proposta Enviada → Negociação → Contrato Assinado → Em Execução → Concluído → Perdido
- 925 empresas distribuídas por estágio
- Drag & Drop para mover empresas entre estágios
- Histórico completo de movimentações
- Alertas para empresas paradas há mais de 7 dias
- Filtros por linha (Tecnologia/Educacional) e consultor

### 5. Prospecção (NOVO!)
- 817 empresas em prospecção
- Gestão de follow-ups
- Status: Novo, Em andamento, Fechado, Perdido
- Sistema Kanban integrado
- Histórico de contatos

### 6. Propostas e Contratos
- Gestão completa de propostas
- Acompanhamento de contratos
- Status de pagamento

### 7. Cronogramas
- Planejamento de projetos
- Alocação de consultores
- Visualização mensal

### 8. Linha Tecnologia e Educacional
- 2.940 programas tecnológicos
- 266 programas educacionais
- Acompanhamento completo do ciclo

### 9. Relatórios
- Exportação em PDF e Excel
- Relatórios de propostas, contratos e cronogramas
- Relatórios analíticos

### 10. Chatbot com IA
- Integração com OpenAI
- Consultas sobre dados do sistema
- Análises e insights

### 11. Automações de Email (NOVO!)
- Gestão de contatos de email
- Criação de campanhas de email marketing
- Seleção múltipla de destinatários
- Upload de anexos (PDFs, imagens, documentos)
- Sistema de envio em massa (requer configuração de provedor)
- Estatísticas de envio e monitoramento
- Status de campanhas: Rascunho, Pronta, Enviada

## 🗄️ Banco de Dados

### PostgreSQL Local (Replit)
- Configurado automaticamente
- Dados preservados entre reinicializações
- 27 tabelas com relacionamentos

### Railway PostgreSQL
- Veja o arquivo `RAILWAY_SETUP.md` para instruções completas
- Migração automática de tabelas
- Importação automática de dados na primeira inicialização
- Dados permanentes

## 🔧 Tecnologias

- **Backend:** FastAPI 0.119.0
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Python:** 3.11
- **IA:** OpenAI GPT
- **Relatórios:** ReportLab (PDF), OpenPyXL (Excel)

## 📁 Estrutura do Projeto

```
workspace/
├── app/
│   ├── main.py                    # Aplicação principal FastAPI
│   ├── database.py                # Configuração do banco de dados
│   ├── models/
│   │   └── models.py              # Modelos SQLAlchemy (27 tabelas)
│   ├── routes/                    # Rotas da API (18 módulos)
│   │   ├── auth.py               # Autenticação
│   │   ├── empresas.py           # Gestão de empresas
│   │   ├── consultores.py        # Gestão de consultores
│   │   ├── propostas.py          # Propostas comerciais
│   │   ├── contratos.py          # Contratos
│   │   ├── cronogramas.py        # Cronogramas
│   │   ├── pipeline.py           # Pipeline Kanban
│   │   ├── prospeccao.py         # Prospecção
│   │   ├── automacoes.py         # Automações de Email
│   │   └── ...                   # Outros módulos
│   ├── static/                    # Arquivos estáticos
│   │   ├── css/style.css
│   │   └── js/                   # JavaScript por página
│   ├── templates/                 # Templates HTML (19 páginas)
│   ├── seed_data.py              # Importação de dados iniciais
│   └── import_prospeccao_pipeline.py  # Importação pipeline/prospecção
├── attached_assets/               # Planilhas Excel de dados
├── pyproject.toml                 # Dependências Python
├── RAILWAY_SETUP.md              # Guia de setup Railway
├── AUTOMACOES_EMAIL.md           # Guia de automações de email
└── replit.md                      # Este arquivo
```

## 🚀 Como Funciona a Inicialização

### Primeira Vez
1. Sistema cria todas as 23 tabelas automaticamente
2. Importa dados de todas as planilhas Excel:
   - Contatos
   - Empresas
   - Consultores
   - Linha Tecnologia
   - Linha Educacional
   - Cronogramas
   - **Pipeline Kanban** (925 empresas)
   - **Prospecção** (817 empresas)
3. Cria usuário admin padrão
4. Sistema fica pronto para uso

### Reinicializações
1. Sistema verifica estrutura do banco
2. **NÃO reimporta dados** (preserva tudo)
3. Adiciona apenas colunas/tabelas novas se necessário
4. Mantém todos os dados existentes

## 🔄 Importação de Dados

### Automática no Startup
O sistema importa automaticamente dados das planilhas em `attached_assets/`:
- `contats_*.xlsx` → Tabela contatos
- `empresas_*.xlsx` → Tabela empresas  
- `crnograma principal jef_*.xlsx` → Tabela alocacoes_cronograma
- `linha tecnologia_*.xlsx` → Tabelas linha_tecnologia, company_pipeline, prospeccao
- `linha educacional_*.xlsx` → Tabelas linha_educacional, company_pipeline

### Segurança dos Dados
- ✅ Importação acontece apenas uma vez
- ✅ Dados marcados com `dados_iniciais=True` não são sobrescritos
- ✅ Sistema detecta dados existentes e pula reimportação
- ✅ Rollback automático em caso de erro

## 📊 Tabelas do Banco de Dados

1. **usuarios** - Usuários do sistema (Admin, Consultor, Financeiro)
2. **empresas** - Cadastro de empresas
3. **consultores** - Cadastro de consultores
4. **propostas** - Propostas comerciais
5. **cronogramas** - Cronogramas de execução
6. **tarefas** - Tarefas dos cronogramas
7. **contratos** - Contratos assinados
8. **feriados** - Calendário de feriados
9. **alocacoes_cronograma** - Alocação de consultores por dia
10. **contatos** - Contatos de empresas
11. **linha_tecnologia** - Programas de tecnologia
12. **linha_educacional** - Programas educacionais
13. **prospeccao** - Empresas em prospecção
14. **followups** - Follow-ups de prospecção
15. **carteira_grm** - Carteira GRM
16. **pesquisas_satisfacao** - Pesquisas de satisfação
17. **solucoes** - Catálogo de soluções
18. **stages** - Estágios do pipeline Kanban
19. **company_pipeline** - Empresas no pipeline
20. **company_stage_history** - Histórico de movimentação no pipeline
21. **notes** - Notas sobre empresas
22. **attachments** - Anexos de documentos
23. **activities** - Log de atividades do sistema
24. **email_contatos** - Contatos para email marketing (NOVO!)
25. **campanhas_email** - Campanhas de email (NOVO!)
26. **campanha_destinatarios** - Destinatários das campanhas (NOVO!)
27. **anexos_email** - Anexos de emails (NOVO!)

## 🛠️ Manutenção

### Adicionar Novos Dados
1. Coloque a planilha Excel em `attached_assets/`
2. Modifique `seed_data.py` ou `import_prospeccao_pipeline.py`
3. Reinicie o servidor

### Backup de Dados
```bash
# Exportar banco PostgreSQL
pg_dump $DATABASE_URL > backup.sql

# Restaurar
psql $DATABASE_URL < backup.sql
```

### Logs do Sistema
- Verificação de tabelas no startup
- Importação de dados
- Erros e avisos

## 🌐 Deploy para Produção

Veja `RAILWAY_SETUP.md` para instruções completas de deploy no Railway.

### Configuração Recomendada
- PostgreSQL no Railway
- Variável `DATABASE_URL` configurada
- Todas as planilhas em `attached_assets/`
- Sistema importa dados automaticamente na primeira vez

## 📞 Contato

Sistema desenvolvido para gestão de relacionamento industrial v1.03

---

**Última atualização:** 22/10/2025
**Status:** ✅ Totalmente funcional com pipeline kanban, prospecção e automações de email
