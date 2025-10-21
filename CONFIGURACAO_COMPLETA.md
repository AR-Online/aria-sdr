# ✅ ARIA-SDR - Configuração Completa

## 🎯 Status Atual

### ✅ Componentes Funcionando
- **Backend FastAPI**: Rodando em http://localhost:8000
- **Frontend Agent UI**: Rodando em http://localhost:3000
- **Supabase API REST**: Conectado e funcionando
- **CORS**: Configurado para comunicação frontend-backend
- **Endpoints Agent UI**: Implementados e funcionando

### 📋 Endpoints Disponíveis
| Endpoint | Método | Status | Descrição |
|----------|---------|--------|-----------|
| `/healthz` | GET | ✅ | Health check |
| `/agents` | GET | ✅ | Lista agentes disponíveis |
| `/teams` | GET | ✅ | Lista teams (vazio por enquanto) |
| `/sessions` | GET | ✅ | Lista sessões de conversa |
| `/agents/{id}/runs` | POST | ✅ | Executa agente com streaming |
| `/assist/routing` | POST | ✅ | Endpoint de routing interno |

### 🔧 Alterações Realizadas

#### 1. **main.py**
- ✅ Adicionado `CORSMiddleware` para comunicação frontend-backend
- ✅ Criado endpoint `/agents` que retorna agente ARIA-SDR
- ✅ Criado endpoint `/teams` (retorna lista vazia)
- ✅ Criado endpoint `/sessions` para histórico de conversas
- ✅ Implementado endpoint `/agents/{agent_id}/runs` com streaming SSE
  - Processa mensagens através da lógica de routing
  - Suporta RAG quando disponível
  - Fallback para LLM direto quando RAG falha
  - Retorna resposta em formato Server-Sent Events

#### 2. **setup_supabase.py** (NOVO)
Script automatizado para configurar o Supabase:
- Testa conexão com PostgreSQL
- Cria tabelas necessárias
- Configura extensão pgvector
- Verifica status das tabelas

**Uso:**
```bash
python setup_supabase.py
```

#### 3. **supabase_schema.sql** (NOVO)
Schema SQL completo com:
- **Tabela `aria_chunks`**: Armazenamento de embeddings (RAG)
  - Suporta vetores de 1536 dimensões (OpenAI)
  - Índice IVFFlat para busca vetorial
  - Busca full-text em português
- **Tabela `aria_sessions`**: Gerenciamento de sessões/conversas
  - Suporta múltiplos canais (web, whatsapp, etc)
  - Metadados em JSONB
- **Tabela `aria_messages`**: Histórico de mensagens
  - Relacionada com sessões
  - Roles: user, assistant, system
- **Row Level Security (RLS)**: Habilitado
- **Triggers**: Auto-update de `updated_at`

### 📦 Arquivos Criados/Modificados

```
✅ main.py                    - Backend principal (MODIFICADO)
✅ setup_supabase.py          - Script de setup (NOVO)
✅ supabase_schema.sql        - Schema do banco (NOVO)
✅ .env                       - Credenciais Supabase adicionadas
❌ .env_temp                  - Removido (cleanup)
❌ test_supabase_api.py       - Removido (cleanup)
```

---

## 🚀 Como Usar

### 1. Iniciar o Sistema

```powershell
# Terminal 1 - Backend
cd d:\-ARIA-Agno\aria-platform
.\teste_local.ps1

# Terminal 2 - Frontend (já deve estar rodando)
cd d:\-ARIA-Agno\aria-platform\aria-agent-ui
npm run dev
```

### 2. Acessar Interface
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs

---

## ⚠️ PRÓXIMOS PASSOS (Amanhã)

### 1. Criar Tabelas no Supabase

O banco de dados Supabase está conectado, mas as **tabelas ainda não foram criadas**.

**Instruções:**

1. Acesse o SQL Editor do Supabase:
   ```
   https://supabase.com/dashboard/project/nywykslatlripxpiehfb/editor/sql
   ```

2. Abra o arquivo `supabase_schema.sql` no seu editor

3. **Copie TODO o conteúdo** do arquivo

4. **Cole no SQL Editor** do Supabase

5. **Clique em "Run"** para executar

6. Aguarde a mensagem de sucesso

**Resultado esperado:**
- ✅ Extensão `vector` instalada
- ✅ Tabelas `aria_chunks`, `aria_sessions`, `aria_messages` criadas
- ✅ Índices para busca vetorial e full-text criados
- ✅ RLS habilitado
- ✅ 1 registro de exemplo inserido

### 2. Testar Funcionalidade RAG

Após criar as tabelas, teste se o RAG está funcionando:

```bash
# Executar teste
cd d:\-ARIA-Agno\aria-platform
.\agno_env\Scripts\Activate.ps1
pytest tests/test_migration_equivalence.py::TestSimilarity::test_rag_context -v
```

**Se der erro "relation aria_chunks does not exist":**
→ Volte ao passo 1 e execute o `supabase_schema.sql`

### 3. Popular Base de Conhecimento

Execute o script de ingestão de FAQs:

```bash
python ingest_supabase.py
```

Isso vai:
- Ler o arquivo de FAQs
- Gerar embeddings com OpenAI
- Inserir na tabela `aria_chunks`
- Habilitar busca semântica

### 4. Testar Chat Completo

Acesse http://localhost:3000 e teste:

**Testes Básicos:**
- "Olá, como você pode me ajudar?"
- "Qual é o seu nome?"
- "Me conte uma piada"

**Testes com RAG (após popular):**
- "O que é a AR Online?"
- "Como funciona a apostila eletrônica?"
- "Quais serviços vocês oferecem?"

---

## 🔍 Verificação de Status

### Verificar Backend
```powershell
curl http://localhost:8000/healthz
curl http://localhost:8000/agents
```

### Verificar Supabase
```powershell
.\agno_env\Scripts\Activate.ps1
python test_supabase_api.py
```

### Verificar Tabelas
Após executar o schema SQL, você pode verificar no Supabase:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'aria_%';
```

---

## 📊 Configurações do Supabase

### Credenciais (já no .env)
```bash
SUPABASE_URL=https://nywykslatlripxpiehfb.supabase.co
SUPABASE_HOST=db.nywykslatlripxpiehfb.supabase.co
SUPABASE_PORT=5432
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=2026*RealizaTI
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
```

### Endpoints Disponíveis
- **Dashboard**: https://supabase.com/dashboard/project/nywykslatlripxpiehfb
- **REST API**: https://nywykslatlripxpiehfb.supabase.co/rest/v1/
- **SQL Editor**: https://supabase.com/dashboard/project/nywykslatlripxpiehfb/editor/sql

---

## 🐛 Resolução de Problemas

### "Failed to fetch" no Chat
✅ **RESOLVIDO** - Endpoint `/agents/{agent_id}/runs` implementado com streaming

### "No agents available"
✅ **RESOLVIDO** - Endpoint `/agents` retornando ARIA-SDR

### "relation aria_chunks does not exist"
⚠️ **PENDENTE** - Execute `supabase_schema.sql` no SQL Editor

### CORS Error
✅ **RESOLVIDO** - CORSMiddleware configurado para localhost:3000 e localhost:8000

---

## 📝 Commits Realizados

### Commit 1: Adiciona endpoints Agent UI
```
feat: Add /agents and /teams endpoints for Agent UI integration
```

### Commit 2: Corrige endpoint de sessões
```
feat: Add /sessions endpoint and fix /agents/{id}/runs
```

### Commit 3: Integração completa (ATUAL)
```
feat: Integra Agent UI com backend e configura Supabase

- Adiciona endpoints /agents, /teams, /sessions para Agent UI
- Implementa endpoint /agents/{agent_id}/runs com streaming
- Configura CORS para comunicacao frontend-backend
- Adiciona setup_supabase.py para configuracao automatica do banco
- Cria supabase_schema.sql com schema completo
- Suporta busca hibrida com pgvector para embeddings
- Implementa fallback quando RAG nao esta disponivel
```

---

## 🎯 Resumo Executivo

### O que está funcionando:
✅ Backend FastAPI com todos endpoints necessários
✅ Frontend Agent UI conectado ao backend
✅ Supabase conectado via API REST
✅ CORS configurado
✅ Streaming de respostas implementado
✅ Fallback para LLM quando RAG não disponível

### O que falta:
⚠️ Criar tabelas no Supabase (executar `supabase_schema.sql`)
⚠️ Popular base de conhecimento (executar `ingest_supabase.py`)
⚠️ Testar funcionalidade RAG completa

### Tempo estimado para conclusão:
- **Criar tabelas**: 2 minutos
- **Popular base**: 5 minutos
- **Testes**: 10 minutos
- **TOTAL**: ~20 minutos

---

## 📞 Informações Técnicas

### Stack Tecnológica
- **Backend**: FastAPI 0.114.1 + Python 3.13.7
- **Frontend**: Next.js 14 + React 18
- **Database**: Supabase (PostgreSQL 15 + pgvector)
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small (1536 dim)
- **Framework**: Agno 2.1.0

### Portas Utilizadas
- Backend: `8000`
- Frontend: `3000`
- Supabase: `5432` (PostgreSQL direto, atualmente desabilitado)

### Variáveis de Ambiente Críticas
```bash
OPENAI_API_KEY=sk-proj-...  # API OpenAI
SUPABASE_URL=https://nywykslatlripxpiehfb.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...  # Acesso admin
API_TOKEN=your-secure-token-here  # Auth interno
```

---

**Data**: 21/10/2025 02:10
**Status**: ✅ Backend funcional, aguardando criação de tabelas Supabase
**Próximo passo**: Executar `supabase_schema.sql` no SQL Editor

