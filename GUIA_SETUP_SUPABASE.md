# 🗄️ Guia Completo - Setup do Supabase

## ✅ Service Role Key Configurada!

A Service Role Key foi recebida e configurada com sucesso:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im55d3lrc2xhdGxyaXB4cGllaGZiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzE5NjYyMSwiZXhwIjoyMDcyNzcyNjIxfQ.RCZsK_fizrwb-om-unYFCpsDV0sQ43FXWtAvnyIZlF4
```

---

## 📋 Próximo Passo: Criar Tabelas no Supabase

### Passo 1: Acessar SQL Editor

Abra no navegador:
```
https://supabase.com/dashboard/project/nywykslatlripxpiehfb/editor/sql
```

### Passo 2: Criar Nova Query

1. Clique em **"New query"** ou **"+"**
2. Cole o conteúdo do arquivo: **`supabase_setup_completo.sql`**

### Passo 3: Executar o Script

1. Clique no botão **"Run"** (▶️) no canto inferior direito
2. Aguarde a execução (pode levar 10-20 segundos)
3. Você verá mensagens de confirmação

---

## 📊 O Que Será Criado

### Tabelas:
1. **`aria_chunks`** - Armazena documentos para RAG
   - Conteúdo de texto
   - Embeddings vetoriais (1536 dim)
   - Metadata em JSONB
   - Campo source para filtros

2. **`aria_sessions`** - Sessões de conversação
   - ID único por usuário/canal
   - Metadata de sessão
   - Timestamps

3. **`aria_messages`** - Histórico de mensagens
   - Vinculado a sessões
   - Role (user/assistant/system)
   - Conteúdo completo

### Índices:
- Busca vetorial (IVFFlat)
- Busca por texto (GIN)
- Busca por source
- Timestamps

### Função RPC:
- **`match_aria_chunks()`** - Busca vetorial híbrida
  - Parâmetros: query_embedding, match_count, filter_source
  - Retorna: chunks similares ordenados

### Dado de Teste:
- 1 chunk de exemplo sobre o ARIA
- Para validar que tudo funciona

---

## ✅ Validação

Após executar o script, você verá:

```sql
Setup concluído! Tabelas criadas:
table_name        
------------------
aria_chunks
aria_messages
aria_sessions

Total de chunks: 1
```

---

## 🧪 Testar o RAG

### Via PowerShell:

```powershell
$body = @{
    question = "O que é ARIA?"
    k = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:7777/rag/query" `
    -Method POST `
    -Body $body `
    -ContentType "application/json" `
    -Headers @{Authorization = "Bearer dtransforma2026"}
```

### Via Frontend:

1. Abra: http://localhost:3000
2. Digite: "O que é ARIA?"
3. O sistema vai buscar na base e responder

---

## 🔧 Configurar Variável de Ambiente

Adicione ao seu arquivo `.env` (ou configure no ambiente):

```env
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im55d3lrc2xhdGxyaXB4cGllaGZiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzE5NjYyMSwiZXhwIjoyMDcyNzcyNjIxfQ.RCZsK_fizrwb-om-unYFCpsDV0sQ43FXWtAvnyIZlF4
```

---

## 🚀 Reiniciar o Servidor

Após criar as tabelas, reinicie o servidor:

```powershell
# Parar o servidor atual (Ctrl+C na janela)
# Iniciar novamente com a nova configuração
$env:SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
python main.py
```

---

## 📚 Adicionar Mais Documentos

Depois de validar que funciona, você pode adicionar mais FAQs:

```sql
INSERT INTO aria_chunks (content, metadata, source) VALUES
(
    'Para enviar mensagens em alto volume (acima de 1200/mês), recomendamos agendar com nossa equipe comercial.',
    '{"categoria": "volume", "tipo": "faq"}',
    'faq'
);
```

Ou use o script `ingest_faqs.py` (se existir).

---

## ❓ FAQ

### P: O script falhou, o que fazer?
**R:** Verifique os erros no SQL Editor. Copie a mensagem de erro e analise.

### P: Posso executar o script múltiplas vezes?
**R:** SIM! O script usa `IF NOT EXISTS` para evitar duplicatas.

### P: Como adiciono embeddings aos chunks?
**R:** Use o script Python ou faça via API OpenAI + Supabase REST.

### P: O RAG funciona sem embeddings?
**R:** Não completamente. Você pode inserir dados sem embeddings, mas a busca vetorial não funcionará.

---

## ✨ Próximos Passos

1. ✅ Execute o SQL no editor do Supabase
2. ✅ Valide que as tabelas foram criadas
3. ✅ Teste o endpoint `/rag/query`
4. ✅ Teste via frontend
5. ✅ Adicione mais documentos (opcional)
6. ✅ Configure ingestão automatizada (opcional)

---

## 🆘 Suporte

Se tiver problemas:
- Verifique `last_error.log`
- Teste a conexão com Supabase
- Verifique se a Service Role Key está correta
- Consulte a documentação: https://supabase.com/docs

---

**Status:** ⏳ Aguardando execução do SQL no Supabase

**Quando concluído:** RAG estará 100% funcional! 🎉

