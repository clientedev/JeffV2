# 🚂 Configuração Railway PostgreSQL

Este guia explica como conectar seu sistema ao PostgreSQL do Railway automaticamente.

## ✅ O Que Acontece Automaticamente

Quando você conectar ao Railway PostgreSQL:

1. **Tabelas são criadas automaticamente** - O sistema verifica e cria as 23 tabelas necessárias
2. **Dados são importados automaticamente** - Na primeira inicialização, todos os dados das planilhas são importados:
   - 3.003 contatos
   - 993 empresas
   - 20 consultores
   - 2.940 registros linha tecnologia
   - 266 registros linha educacional
   - 4.967 alocações de cronograma
   - **925 empresas no pipeline kanban**
   - **817 empresas na prospecção**

3. **Dados são preservados** - Uma vez importados, os dados NÃO são sobrescritos em reinicializações

## 📋 Passos para Conectar ao Railway

### 1. Criar Banco PostgreSQL no Railway

1. Acesse [Railway.app](https://railway.app)
2. Crie um novo projeto ou use um existente
3. Adicione um serviço PostgreSQL
4. Copie a variável `DATABASE_URL`

### 2. Configurar no Replit

No Replit, adicione as seguintes variáveis de ambiente (Secrets):

```
DATABASE_URL=postgresql://postgres:senha@host:port/database
```

**Formato do Railway:**
```
DATABASE_URL=postgresql://postgres.railway.internal:5432/railway
```

### 3. Reiniciar o Sistema

1. Stop o servidor atual
2. Start o servidor novamente
3. O sistema irá:
   - Conectar ao banco Railway
   - Criar todas as tabelas automaticamente
   - Importar todos os dados na primeira vez
   - Manter os dados em reinicializações subsequentes

## 🔍 Verificação

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

O sistema cria automaticamente 23 tabelas:

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

## ⚡ Migrações Futuras

O sistema possui um mecanismo de migração seguro que:

- Adiciona novas colunas automaticamente
- Nunca remove colunas existentes
- Nunca remove tabelas existentes
- Preserva todos os dados

## 🆘 Troubleshooting

### Problema: Dados não aparecem

**Solução:** Verifique os logs do servidor para confirmar a importação:
```
INFO:app.seed_data:Importando dados para pipeline...
INFO:app.seed_data:Importando dados para prospecção...
```

### Problema: Erro de conexão

**Solução:** Verifique se a variável `DATABASE_URL` está correta:
```bash
echo $DATABASE_URL
```

### Problema: Tabelas não criadas

**Solução:** O sistema cria automaticamente no startup. Verifique os logs:
```
✅ Tabelas criadas com sucesso!
```

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do servidor
2. Confirme que a variável `DATABASE_URL` está configurada
3. Reinicie o servidor

---

**Sistema de Relacionamento com a Indústria v1.03**
