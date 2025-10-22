# 📧 Sistema de Automações de Email

## Visão Geral

O sistema de automações de email permite criar e gerenciar campanhas de email marketing, manter uma lista de contatos e enviar emails em massa com anexos.

## ✨ Funcionalidades

### 1. Gestão de Contatos de Email
- Cadastro de contatos com nome, email, empresa, cargo e telefone
- Busca e filtros avançados
- Importação e exportação de contatos
- Status ativo/inativo

### 2. Criação de Campanhas
- Editor de email com campos de título, assunto e corpo
- Seleção múltipla de destinatários
- Upload de anexos (documentos, imagens, PDFs)
- Personalização de remetente

### 3. Gerenciamento de Campanhas
- Visualização de todas as campanhas
- Status: Rascunho, Pronta para Envio, Enviada
- Estatísticas de envio (total de destinatários, enviados, falhas)
- Histórico completo

## 🗄️ Estrutura do Banco de Dados

### Tabelas Criadas

1. **email_contatos** - Contatos de email
   - id, nome, email, empresa, cargo, telefone
   - ativo, observacoes
   - criado_em, atualizado_em

2. **campanhas_email** - Campanhas de email
   - id, titulo, assunto, corpo_email
   - remetente_nome, remetente_email
   - status, data_agendamento, data_envio
   - total_destinatarios, total_enviados, total_falhas
   - usuario_id

3. **campanha_destinatarios** - Destinatários das campanhas
   - id, campanha_id, email_contato_id
   - email, nome, status_envio
   - data_envio, mensagem_erro

4. **anexos_email** - Anexos das campanhas
   - id, campanha_id
   - nome_arquivo, tipo_arquivo, tamanho_bytes
   - caminho_arquivo

## 🚀 Como Usar

### Acessar o Sistema
1. Faça login no sistema
2. No menu lateral, clique em **"Automações Email"** na seção Ferramentas

### Gerenciar Contatos
1. Clique na aba **"Contatos"**
2. Clique em **"Novo Contato"** para adicionar
3. Preencha nome e email (obrigatórios)
4. Adicione informações opcionais: empresa, cargo, telefone, observações
5. Clique em **"Salvar"**

### Criar uma Campanha
1. Clique em **"Nova Campanha"**
2. Preencha:
   - **Título da Campanha** (interno, para organização)
   - **Assunto do Email** (o que o destinatário verá)
   - **Corpo do Email** (conteúdo da mensagem)
   - Opcionalmente: Nome e Email do remetente
3. **Selecione os Destinatários**:
   - Marque os contatos que receberão o email
   - Use a busca para filtrar contatos
4. **Adicione Anexos** (opcional):
   - Clique em "Adicionar Anexos"
   - Selecione os arquivos
5. Escolha uma opção:
   - **Salvar Rascunho**: Salva sem enviar
   - **Preparar para Envio**: Marca como pronta (envio manual após configurar provedor)

## 📨 Configuração do Envio de Emails

Para enviar emails reais, você precisa configurar um provedor de email (SendGrid, Resend ou Gmail).

### Opção 1: SendGrid (Recomendado para Volume)

1. **Criar conta no SendGrid**:
   - Acesse https://sendgrid.com
   - Crie uma conta gratuita (100 emails/dia)
   - Ou conta paga para volume maior

2. **Obter API Key**:
   - No painel do SendGrid, vá em Settings → API Keys
   - Clique em "Create API Key"
   - Escolha "Full Access"
   - Copie a chave gerada

3. **Configurar no Replit**:
   - Use a ferramenta de configuração de integrações do Replit
   - Ou adicione manualmente no Secrets:
     - Nome: `SENDGRID_API_KEY`
     - Valor: Sua chave da API

### Opção 2: Resend (Recomendado para Desenvolvedores)

1. **Criar conta no Resend**:
   - Acesse https://resend.com
   - Crie uma conta

2. **Obter API Key**:
   - No painel, vá em API Keys
   - Clique em "Create API Key"
   - Copie a chave

3. **Configurar no Replit**:
   - Adicione no Secrets:
     - Nome: `RESEND_API_KEY`
     - Valor: Sua chave da API

### Opção 3: Gmail (Para Testes)

1. **Configurar App Password**:
   - Acesse sua conta Google
   - Segurança → Verificação em duas etapas
   - Senhas de app → Criar nova senha
   - Copie a senha gerada

2. **Configurar no Replit**:
   - Adicione nos Secrets:
     - `GMAIL_USER`: seu.email@gmail.com
     - `GMAIL_PASSWORD`: senha de app gerada

## 🔧 Implementação do Envio (Próximo Passo)

Atualmente, o sistema possui toda a estrutura de CRUD (criar, ler, atualizar, deletar) campanhas e contatos. Para implementar o envio real:

### Para SendGrid:
```python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def enviar_com_sendgrid(campanha, destinatario):
    message = Mail(
        from_email=campanha.remetente_email,
        to_emails=destinatario.email,
        subject=campanha.assunto,
        html_content=campanha.corpo_email
    )
    
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        return True
    except Exception as e:
        return False
```

### Para Resend:
```python
import os
import resend

resend.api_key = os.getenv('RESEND_API_KEY')

def enviar_com_resend(campanha, destinatario):
    try:
        resend.Emails.send({
            'from': campanha.remetente_email,
            'to': destinatario.email,
            'subject': campanha.assunto,
            'html': campanha.corpo_email
        })
        return True
    except Exception:
        return False
```

## 📊 Estatísticas e Monitoramento

Após configurar o envio:
- Acompanhe em tempo real quantos emails foram enviados
- Veja quais destinatários receberam com sucesso
- Identifique falhas e mensagens de erro
- Analise taxas de entrega

## 🔒 Segurança

- Apenas usuários autenticados podem acessar o sistema
- Credenciais de API armazenadas com segurança nos Secrets
- Validação de emails antes do envio
- Log completo de todas as ações

## 💡 Dicas de Uso

1. **Teste primeiro**: Crie uma campanha de teste com seu próprio email
2. **Segmente seus contatos**: Use filtros para enviar para grupos específicos
3. **Revise o conteúdo**: Verifique ortografia e links antes de enviar
4. **Monitore os resultados**: Acompanhe as estatísticas após cada envio
5. **Respeite limites**: Verifique os limites do seu plano de email
6. **Lei de SPAM**: Sempre inclua opção de descadastramento

## 🆘 Solução de Problemas

### "Campanhas não aparecem"
- Verifique se está logado
- Recarregue a página
- Verifique o console do navegador por erros

### "Não consigo adicionar destinatários"
- Certifique-se de ter contatos cadastrados
- Verifique se a campanha está em status "Rascunho"

### "Erro ao fazer upload de anexos"
- Verifique o tamanho do arquivo (limite: 10MB por arquivo)
- Certifique-se de que o formato é permitido

### "Emails não são enviados"
- Verifique se configurou a integração de email
- Confirme que as credenciais de API estão corretas
- Verifique os limites do seu plano

## 📈 Próximos Passos

Para envio de emails em produção:
1. Escolha um provedor (SendGrid, Resend ou Gmail)
2. Configure as credenciais nos Secrets do Replit
3. Adicione o código de envio à função `enviar_campanha` em `app/routes/automacoes.py`
4. Teste com uma campanha pequena
5. Monitore os resultados

---

**Sistema desenvolvido como parte do Sistema de Relacionamento com a Indústria v1.03**
