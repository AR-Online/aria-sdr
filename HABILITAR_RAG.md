# 🔐 Como Habilitar RAG (Busca Inteligente)

O projeto já está funcionando, mas para habilitar a funcionalidade completa de RAG (Retrieval-Augmented Generation), você precisa configurar o Supabase completamente.

---

## 📋 O que você precisa

**Service Role Key** do Supabase - Esta é uma chave secreta que dá acesso total ao banco de dados.

---

## 🔍 Como Obter a Service Role Key

### Passo 1: Acessar o Dashboard do Supabase
Abra no navegador: https://supabase.com/dashboard/project/nywykslatlripxpiehfb/settings/api

### Passo 2: Localizar a Key
Na página de Settings > API, você verá duas seções:

1. **Project API keys**
   - `anon` / `public` - ❌ NÃO É ESTA!
   - `service_role` - ✅ É ESTA AQUI!

### Passo 3: Copiar a Service Role Key
- Clique em "Reveal" ou no ícone de olho ao lado de **service_role**
- A chave começará com `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- Copie a chave completa

### Passo 4: Adicionar ao .env
Edite seu arquivo `.env` e adicione:

```env
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im55d3lrc2xhdGxyaXB4cGllaGZiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTYzODI5NjQwMCwiZXhwIjoxOTUzODcyNDAwfQ.SUA_CHAVE_AQUI
```

---

## 🛠️ Criar as Tabelas no Supabase

Depois de adicionar a key, execute:

```powershell
python setup_supabase.py
```

Este script vai:
- ✅ Testar a conexão
- ✅ Criar tabela `aria_chunks` (para documentos/RAG)
- ✅ Criar tabela `aria_sessions` (para conversas)
- ✅ Criar tabela `aria_messages` (para histórico)
- ✅ Criar índices para busca vetorial
- ✅ Habilitar extensão pgvector

---

## 🧪 Testar o RAG

Depois de configurar, teste com:

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

---

## 📊 Alternativa: Usar o SQL Editor do Supabase

Se preferir, você pode criar as tabelas manualmente:

### 1. Acesse o SQL Editor
https://supabase.com/dashboard/project/nywykslatlripxpiehfb/sql/new

### 2. Execute o Script
Copie o conteúdo do arquivo `supabase_schema.sql` e execute no SQL Editor.

### 3. Verificar
Execute no SQL Editor:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'aria_%';
```

Você deve ver:
- `aria_chunks`
- `aria_sessions`
- `aria_messages`

---

## 🔒 Segurança

⚠️ **IMPORTANTE:**

- A **Service Role Key** tem acesso total ao banco
- **NUNCA** exponha esta chave em código frontend
- **NUNCA** commite esta chave no Git
- Use apenas em código backend (servidor)
- Mantenha sempre no arquivo `.env` (que deve estar no `.gitignore`)

---

## ❓ Problemas Comuns

### Erro: "Could not translate host name"
**Solução:** Verifique sua conexão de internet. O Supabase está na nuvem.

### Erro: "permission denied for table aria_chunks"
**Solução:** Você está usando a `anon` key ao invés da `service_role` key.

### Erro: "relation aria_chunks does not exist"
**Solução:** Execute `python setup_supabase.py` para criar as tabelas.

### Erro: "extension pgvector does not exist"
**Solução:** Execute no SQL Editor: `CREATE EXTENSION IF NOT EXISTS vector;`

---

## 📈 Depois de Habilitar RAG

Com o RAG habilitado, você poderá:

1. **Fazer Ingestão de Documentos**
   ```powershell
   python ingest_faqs.py
   ```

2. **Buscar com Contexto**
   - O sistema vai buscar documentos relevantes
   - Usar embeddings vetoriais
   - Retornar respostas mais precisas

3. **Usar no Roteamento**
   - O endpoint `/assist/routing` automaticamente usará RAG
   - Quando detectar perguntas, vai buscar na base
   - Respostas serão contextualizadas

---

## ✅ Checklist

- [ ] Acessei o dashboard do Supabase
- [ ] Copiei a Service Role Key (não a anon key!)
- [ ] Adicionei ao arquivo `.env`
- [ ] Executei `python setup_supabase.py`
- [ ] Verifiquei que as tabelas foram criadas
- [ ] Testei o endpoint `/rag/query`
- [ ] Funcionou! 🎉

---

**Atenção:** Mesmo sem RAG, o sistema já está 100% funcional para roteamento, chat com IA e classificação de volume!

O RAG é uma funcionalidade **adicional** que melhora as respostas baseando-se em documentos específicos.

