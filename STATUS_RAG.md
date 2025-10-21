# 🔍 Status da Integração RAG - ARIA-SDR

## ❓ O Sistema Está Integrado com RAG?

**Resposta:** ⚠️ **PARCIALMENTE**

---

## 📊 Status Atual do RAG

### ✅ O que ESTÁ configurado:

1. **Código RAG Implementado**
   - ✅ Função `fetch_rag_context()` no `main.py`
   - ✅ Endpoint `/rag/query` disponível
   - ✅ Detecção de quando usar RAG (`want_rag()`)
   - ✅ Integração no fluxo de roteamento
   - ✅ Suporte a embeddings OpenAI

2. **OpenAI Configurado**
   - ✅ API Key configurada
   - ✅ Modelo de embeddings: `text-embedding-3-small`
   - ✅ Dimensão: 1536

3. **Supabase Configurado Parcialmente**
   - ✅ URL: https://nywykslatlripxpiehfb.supabase.co
   - ✅ Database: postgres
   - ✅ User/Password: Configurados
   - ❌ **Service Role Key**: NÃO configurada (FALTA!)

### ❌ O que NÃO está funcionando:

1. **Service Role Key do Supabase**
   - ❌ Chave necessária para acessar o banco
   - ❌ Sem ela, o RAG não consegue buscar documentos
   - ❌ Endpoint `/rag/query` vai falhar

2. **Tabelas do Banco**
   - ❓ Não sabemos se existem (precisa da key para verificar)
   - ❓ Tabela `aria_chunks` pode não existir

3. **Base de Conhecimento**
   - ❓ Nenhum documento foi ingerido ainda
   - ❓ Não há dados para buscar

---

## 🔄 Como o Sistema Funciona AGORA (Sem RAG)

### Fluxo Atual:

```
Usuário → Frontend
    ↓
Backend recebe mensagem
    ↓
Verifica se precisa RAG (want_rag())
    ↓
    ├─ Se detectar palavras-chave (como, funciona, preço)
    │  └─ TENTA usar RAG → FALHA (sem Service Role Key)
    │     └─ Fallback: Usa OpenAI diretamente
    │
    └─ Se não detectar
       └─ Usa regras + OpenAI diretamente
    ↓
Retorna resposta
```

### Palavras-chave que acionam RAG:
- "como"
- "funciona"
- "preço"
- "prazo"
- "o que é"
- "qual"
- "como faço"

---

## ✅ O que FUNCIONA sem RAG:

1. **Roteamento Inteligente**
   - Detecta "envio" vs "recebimento"
   - Funciona 100%

2. **Classificação de Volume**
   - Detecta alto/baixo volume
   - Threshold: 1200 mensagens/mês
   - Funciona 100%

3. **Chat com OpenAI**
   - Respostas contextualizadas
   - Modelo: gpt-4o-mini
   - Funciona 100%

4. **Webhooks**
   - GitLab, Mindchat
   - Funciona 100%

---

## 🚀 Como HABILITAR o RAG Completo

### Passo 1: Obter Service Role Key

1. Acesse: https://supabase.com/dashboard/project/nywykslatlripxpiehfb/settings/api

2. Procure por: **"service_role"** (secret)
   - ⚠️ NÃO é a `anon` key!
   - A chave começa com `eyJ...`

3. Copie a chave completa

### Passo 2: Adicionar ao .env

Crie/edite o arquivo `.env` e adicione:

```env
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Passo 3: Criar as Tabelas

Execute o script de setup:

```powershell
python setup_supabase.py
```

Este script vai:
- ✅ Testar a conexão
- ✅ Criar tabela `aria_chunks`
- ✅ Criar tabela `aria_sessions`
- ✅ Criar tabela `aria_messages`
- ✅ Criar índices para busca vetorial
- ✅ Habilitar extensão pgvector

### Passo 4: Fazer Ingestão de Documentos

Execute o script de ingestão (se existir FAQ):

```powershell
python ingest_faqs.py
```

Ou crie documentos manualmente no banco.

### Passo 5: Reiniciar o Servidor

```powershell
# Parar o servidor atual (Ctrl+C na janela)
# Iniciar novamente
python main.py
```

---

## 🧪 Como Testar o RAG (Depois de Configurado)

### Via API Direta:

```powershell
$body = @{
    query = "Como funciona o sistema ARIA?"
    k = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:7777/rag/query" `
    -Method POST `
    -Body $body `
    -ContentType "application/json" `
    -Headers @{Authorization = "Bearer dtransforma2026"}
```

### Via Frontend:

1. Abra http://localhost:3000
2. Digite: "Como funciona o sistema ARIA?"
3. O sistema vai:
   - Detectar que é uma pergunta
   - Buscar na base de conhecimento
   - Retornar resposta baseada em documentos

---

## 📊 Comparação: Com vs Sem RAG

| Aspecto | Sem RAG (Atual) | Com RAG (Completo) |
|---------|-----------------|-------------------|
| Roteamento | ✅ Funciona | ✅ Funciona |
| Volume | ✅ Funciona | ✅ Funciona |
| Perguntas FAQ | ⚠️ OpenAI genérico | ✅ Base específica |
| Precisão | 🟡 Boa | 🟢 Excelente |
| Fontes | ❌ Não cita | ✅ Cita documentos |
| Personalização | 🟡 Limitada | 🟢 Total |

---

## 💡 Recomendação

### Para Uso Imediato:
**Não precisa do RAG!**

O sistema está 100% funcional para:
- Roteamento de mensagens
- Classificação de volume
- Chat inteligente
- Webhooks

### Para Uso em Produção:
**Configure o RAG!**

Benefícios:
- Respostas mais precisas
- Baseadas em seus documentos
- Cita fontes
- Menos alucinações
- Mais confiável

---

## 🔐 Segurança da Service Role Key

⚠️ **IMPORTANTE:**

A Service Role Key:
- Tem acesso TOTAL ao banco
- Deve ser mantida SECRETA
- NUNCA exponha no frontend
- NUNCA commite no Git
- Use APENAS no backend
- Mantenha no `.env` (no `.gitignore`)

---

## 📝 Checklist RAG

- [ ] Obtive a Service Role Key do Supabase
- [ ] Adicionei no arquivo `.env`
- [ ] Executei `python setup_supabase.py`
- [ ] Verifiquei que as tabelas foram criadas
- [ ] Fiz ingestão de documentos (FAQs)
- [ ] Testei o endpoint `/rag/query`
- [ ] Testei via frontend
- [ ] RAG funcionando! 🎉

---

## ❓ FAQ

### P: O sistema funciona sem RAG?
**R:** SIM! Está 100% funcional. RAG é um adicional.

### P: Por que preciso da Service Role Key?
**R:** Para acessar o banco de dados Supabase onde ficam os documentos.

### P: É seguro usar a Service Role Key?
**R:** SIM, mas apenas no backend. Nunca exponha no frontend.

### P: Quanto tempo leva para configurar?
**R:** 5-10 minutos se você tiver a key.

### P: Posso usar outro banco?
**R:** SIM! O código pode ser adaptado para PostgreSQL direto ou outro vector DB.

---

## 🆘 Erros Comuns

### "relation aria_chunks does not exist"
**Solução:** Execute `python setup_supabase.py`

### "RPC match failed: 404"
**Solução:** Crie a função RPC no Supabase (está no `supabase_schema.sql`)

### "Invalid API key"
**Solução:** Verifique se está usando a `service_role` key, não a `anon` key

---

## ✅ Resumo

**Status Atual:** ⚠️ RAG PARCIALMENTE CONFIGURADO

**Funciona agora:** ✅ SIM (sem RAG, mas totalmente funcional)

**Precisa fazer:** 
1. Obter Service Role Key do Supabase
2. Adicionar no `.env`
3. Executar `setup_supabase.py`
4. Fazer ingestão de documentos

**Guia completo:** Veja `HABILITAR_RAG.md`

---

*Última atualização: 2025-10-21*

