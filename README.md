# Núcleo de Tecnologia 1.03

Sistema completo de gestão industrial para controle de propostas, contratos, cronogramas, empresas e consultores.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Instalação](#instalação)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API Endpoints](#api-endpoints)
- [Contribuindo](#contribuindo)

## 🎯 Sobre o Projeto

O **Núcleo de Tecnologia** é um sistema web completo de gestão industrial desenvolvido para gerenciar todo o ciclo de negócios, desde o primeiro contato com empresas até a conclusão de contratos e projetos. O sistema oferece funcionalidades avançadas de BI (Business Intelligence), chatbot com IA, automações de e-mail, pipeline Kanban e muito mais.

### Características Principais

- 🔐 **Autenticação segura** com controle de acesso baseado em funções
- 📊 **Dashboard BI** com estatísticas e gráficos interativos
- 🤖 **Chatbot com IA** (Groq LLaMA 3.3) para consultas em linguagem natural
- 📧 **Automações de e-mail** com campanhas e templates
- 🎯 **Pipeline Kanban** para gestão visual de empresas
- 📈 **Relatórios** em PDF e Excel
- 🔔 **Sistema de alertas** para contratos, projetos e propostas
- 📥 **Importação em massa** de dados via Excel/CSV

## ✨ Funcionalidades

### 1. Gestão de Empresas
- Cadastro completo de empresas com dados detalhados (CNPJ, endereço, porte, segmento)
- Filtros avançados por porte, região, zona, município, estado e área
- Busca inteligente por nome, CNPJ ou sigla
- Exportação de dados em PDF e Excel
- Visualização de histórico de propostas e contratos

### 2. Gestão de Consultores
- Cadastro de consultores com informações de contato
- Controle de status ativo/inativo
- Visualização de produtividade e estatísticas individuais
- Dashboard personalizado por consultor
- Histórico de propostas e projetos

### 3. Gestão de Propostas
- Criação e acompanhamento de propostas comerciais
- Status: Em andamento, Fechado, Perdido
- Cálculo automático de taxa de conversão
- Identificação de propostas paradas (+30 dias)
- Filtros por consultor, período e status
- Estatísticas detalhadas de performance

### 4. Gestão de Cronogramas
- Planejamento de projetos com tarefas e prazos
- Cálculo automático de percentual de conclusão
- Gerenciamento de tarefas com status e responsáveis
- Alertas para prazos próximos ou vencidos
- Exportação de cronogramas em PDF e Excel
- Visualização de alocações de recursos

### 5. Gestão de Contratos
- Registro de contratos com dados financeiros
- Controle de status de pagamento (Pago, Pendente, Vencido)
- Cálculo de faturamento por período
- Alertas de contratos a vencer (7 dias)
- Relatórios financeiros consolidados

### 6. Business Intelligence (BI)
- **Dashboard Principal**
  - Total de propostas, empresas e consultores
  - Receita total e mensal
  - Gráficos de propostas por status
  - Produtividade de consultores
  
- **Análises Consolidadas**
  - Estatísticas de Linha Tecnologia
  - Estatísticas de Linha Educacional
  - Distribuição mensal de propostas e receita
  - Top consultores por volume

### 7. Chatbot com IA
- Integração com Groq AI (modelo LLaMA 3.3 70B)
- Consultas em linguagem natural sobre:
  - Contratos vencendo
  - Projetos ativos
  - Propostas paradas
  - Receita e faturamento
  - Estatísticas gerais do sistema
- Respostas contextualizadas em português brasileiro

### 8. Sistema de Alertas
- **Contratos a Vencer**: Alertas para contratos vencendo em 7 dias
- **Cronogramas Atrasados**: Projetos com prazo próximo ou vencido
- **Propostas Paradas**: Propostas em andamento há mais de 30 dias
- Dashboard consolidado de alertas críticos

### 9. Gestão de Contatos
- Cadastro de contatos com múltiplos endereços de e-mail
- Organização por empresa
- Exportação em PDF e Excel
- Integração com campanhas de e-mail

### 10. Linha Tecnologia
- Gestão específica de projetos tecnológicos
- Acompanhamento de etapas e status
- Estatísticas de valor e volume
- Análise por consultor

### 11. Linha Educacional
- Gestão de projetos educacionais
- Controle de propostas e contratos
- Relatórios específicos da linha
- Análise de performance

### 12. Pipeline Kanban
- Gestão visual de empresas em diferentes estágios
- Drag-and-drop para mover empresas entre etapas
- Histórico completo de movimentações
- Notas e anexos por empresa
- Registro de atividades
- Importação automática de outras linhas

### 13. Gerenciamento de Etapas
- Criação e edição de etapas customizadas
- Definição de cores e ordem
- Controle de etapas ativas/inativas

### 14. Automações de E-mail
- **Gerenciamento de Contatos**
  - Lista segmentada de contatos
  - Importação em massa
  - Grupos e tags

- **Campanhas de E-mail**
  - Criação de campanhas com templates
  - Envio em massa ou agendado
  - Anexos de arquivos
  - Rastreamento de envios
  
- **Configuração SMTP**
  - Configuração segura de servidor SMTP
  - Criptografia de credenciais
  - Teste de conectividade

### 15. Importação de Dados
- Importação de empresas via Excel/CSV
- Importação de propostas em lote
- Importação de cronogramas e tarefas
- Validação automática de dados
- Relatório de erros e sucessos

### 16. Relatórios
- **Relatórios de Propostas**
  - Consolidados por período
  - Por consultor
  - Exportação PDF/Excel
  
- **Relatórios de Contratos**
  - Financeiro detalhado
  - Status de pagamentos
  - Faturamento por período
  
- **Relatórios de Cronogramas**
  - Andamento de projetos
  - Tarefas por consultor
  - Análise de prazos

- **Relatórios Analíticos**
  - Pesquisas de satisfação
  - Carteira GRM
  - Análises consolidadas

## 🚀 Tecnologias Utilizadas

### Backend
- **Python 3.11**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **PostgreSQL** - Banco de dados relacional
- **Pydantic** - Validação de dados
- **Python-Jose** - Autenticação JWT
- **Passlib + Bcrypt** - Criptografia de senhas
- **Groq AI** - Integração com IA (LLaMA 3.3)

### Frontend
- **HTML5 + CSS3**
- **JavaScript (Vanilla)**
- **Jinja2** - Templates
- **Chart.js** - Gráficos interativos (via Plotly)

### Bibliotecas de Produtividade
- **Pandas** - Manipulação de dados
- **OpenPyXL** - Geração de Excel
- **ReportLab** - Geração de PDF
- **Python-Multipart** - Upload de arquivos
- **Cryptography** - Segurança adicional

### DevOps
- **Uvicorn** - Servidor ASGI
- **Python-dotenv** - Gerenciamento de variáveis de ambiente

## 📦 Instalação

### Pré-requisitos
- Python 3.11+
- PostgreSQL 12+
- pip ou uv (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd nucleo-tecnologia
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:
```env
# Banco de Dados
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nucleo_tecnologia

# JWT
SECRET_KEY=sua-chave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Groq AI (opcional)
GROQ_API_KEY=sua-chave-groq-aqui

# SMTP (opcional, para automações)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app
```

4. **Inicialize o banco de dados**

O sistema cria automaticamente todas as tabelas na primeira execução.

5. **Execute o servidor**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

6. **Acesse o sistema**

Abra o navegador em `http://localhost:5000`

**Credenciais padrão:**
- Email: `admin@sistema.com`
- Senha: `admin123`

## 💡 Uso

### Primeiro Acesso

1. Faça login com as credenciais padrão
2. Altere a senha do administrador
3. Crie usuários adicionais conforme necessário
4. Importe dados iniciais (empresas, consultores) via Excel

### Fluxo de Trabalho Típico

1. **Cadastro de Empresas**: Importe ou cadastre empresas manualmente
2. **Cadastro de Consultores**: Adicione os consultores da equipe
3. **Gestão de Pipeline**: Mova empresas pelo pipeline Kanban
4. **Criação de Propostas**: Registre propostas para empresas
5. **Acompanhamento**: Use o dashboard para monitorar performance
6. **Contratos**: Registre contratos fechados
7. **Cronogramas**: Planeje e acompanhe projetos
8. **Alertas**: Monitore alertas críticos diariamente

### Uso do Chatbot

Digite perguntas em linguagem natural:
- "Quais contratos estão vencendo?"
- "Quantos projetos estão ativos?"
- "Qual a receita deste mês?"
- "Mostre as propostas paradas"

## 📁 Estrutura do Projeto

```
nucleo-tecnologia/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicação principal FastAPI
│   ├── database.py             # Configuração do banco de dados
│   ├── auth.py                 # Autenticação e autorização
│   ├── seed_data.py            # Dados iniciais
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py           # Modelos SQLAlchemy
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py          # Esquemas Pydantic
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py             # Rotas de autenticação
│   │   ├── empresas.py         # Rotas de empresas
│   │   ├── consultores.py      # Rotas de consultores
│   │   ├── propostas.py        # Rotas de propostas
│   │   ├── cronogramas.py      # Rotas de cronogramas
│   │   ├── contratos.py        # Rotas de contratos
│   │   ├── bi.py               # Rotas de BI
│   │   ├── chatbot.py          # Rotas do chatbot
│   │   ├── alertas.py          # Rotas de alertas
│   │   ├── contatos.py         # Rotas de contatos
│   │   ├── importacao.py       # Rotas de importação
│   │   ├── relatorios.py       # Rotas de relatórios
│   │   ├── pipeline.py         # Rotas do pipeline
│   │   ├── automacoes.py       # Rotas de automações
│   │   └── ...
│   ├── templates/              # Templates HTML
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── empresas.html
│   │   └── ...
│   └── static/                 # Arquivos estáticos
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   ├── dashboard.js
│       │   └── ...
│       └── images/
├── data_files/                 # Arquivos de dados para importação
├── requirements.txt            # Dependências Python
├── .env                        # Variáveis de ambiente (não commitado)
├── .gitignore
└── README.md
```

## 🔌 API Endpoints

### Autenticação
- `POST /api/login` - Login de usuário
- `GET /api/usuarios/me` - Obter usuário atual
- `POST /api/usuarios` - Criar novo usuário (Admin)
- `GET /api/usuarios` - Listar usuários (Admin)

### Empresas
- `GET /api/empresas` - Listar empresas
- `POST /api/empresas` - Criar empresa
- `GET /api/empresas/{id}` - Obter empresa
- `PUT /api/empresas/{id}` - Atualizar empresa
- `DELETE /api/empresas/{id}` - Deletar empresa
- `GET /api/empresas/exportar/pdf` - Exportar PDF
- `GET /api/empresas/exportar/excel` - Exportar Excel

### Consultores
- `GET /api/consultores` - Listar consultores
- `POST /api/consultores` - Criar consultor
- `GET /api/consultores/{id}` - Obter consultor
- `PUT /api/consultores/{id}` - Atualizar consultor
- `DELETE /api/consultores/{id}` - Desativar consultor
- `GET /api/consultores/{id}/detalhes` - Estatísticas do consultor

### Propostas
- `GET /api/propostas` - Listar propostas
- `POST /api/propostas` - Criar proposta
- `GET /api/propostas/{id}` - Obter proposta
- `PUT /api/propostas/{id}` - Atualizar proposta
- `DELETE /api/propostas/{id}` - Deletar proposta
- `GET /api/propostas/estatisticas` - Estatísticas de propostas

### Cronogramas
- `GET /api/cronogramas` - Listar cronogramas
- `POST /api/cronogramas` - Criar cronograma
- `GET /api/cronogramas/{id}` - Obter cronograma
- `PUT /api/cronogramas/{id}` - Atualizar cronograma
- `GET /api/cronogramas/alertas` - Cronogramas com alertas
- `GET /api/cronogramas/{id}/tarefas` - Listar tarefas
- `POST /api/cronogramas/{id}/tarefas` - Criar tarefa

### Contratos
- `GET /api/contratos` - Listar contratos
- `POST /api/contratos` - Criar contrato
- `GET /api/contratos/{id}` - Obter contrato
- `PUT /api/contratos/{id}` - Atualizar contrato
- `DELETE /api/contratos/{id}` - Deletar contrato
- `GET /api/contratos/faturamento` - Relatório de faturamento
- `GET /api/contratos/alertas` - Contratos com alertas

### Business Intelligence
- `GET /api/bi/dashboard` - Dados do dashboard
- `GET /api/bi/propostas-por-status` - Propostas agrupadas
- `GET /api/bi/produtividade-consultores` - Produtividade
- `GET /api/bi/linhas/consolidado` - Estatísticas consolidadas

### Chatbot
- `POST /api/chatbot/perguntar` - Fazer pergunta ao chatbot

### Alertas
- `GET /api/alertas/todos` - Todos os alertas
- `GET /api/alertas/resumo` - Resumo de alertas críticos

### Importação
- `POST /api/importacao/empresas` - Importar empresas
- `POST /api/importacao/propostas` - Importar propostas
- `POST /api/importacao/cronogramas` - Importar cronogramas

### Pipeline
- `GET /api/pipeline/stages` - Listar etapas
- `GET /api/pipeline/companies` - Empresas no pipeline
- `POST /api/pipeline/companies/{id}/move` - Mover empresa
- `GET /api/pipeline/companies/{id}/history` - Histórico
- `POST /api/pipeline/companies/{id}/notes` - Adicionar nota

### Automações
- `GET /api/automacoes/contatos` - Listar contatos de e-mail
- `POST /api/automacoes/contatos` - Criar contato
- `GET /api/automacoes/campanhas` - Listar campanhas
- `POST /api/automacoes/campanhas` - Criar campanha
- `POST /api/automacoes/campanhas/{id}/enviar` - Enviar campanha
- `GET /api/automacoes/smtp` - Obter config SMTP
- `POST /api/automacoes/smtp` - Salvar config SMTP

## 👥 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é proprietário e confidencial.

## 📞 Suporte

Para suporte técnico ou dúvidas, entre em contato com a equipe de desenvolvimento.

---

**Núcleo de Tecnologia 1.03** - Sistema de Gestão Industrial Completo 🚀
