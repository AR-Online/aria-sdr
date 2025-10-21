# 🗄️ Configuração do Supabase - ARIA-SDR

## 📋 Credenciais Recebidas

```
Host:     db.nywykslatlripxpiehfb.supabase.co
Port:     5432
Database: postgres
User:     postgres
Password: [PENDENTE - Você precisa fornecer]
```

## 🔧 Como Configurar

### Opção 1: Script Automático (Recomendado)

Execute o script que criamos:

```powershell
.\configurar_supabase.ps1
```

O script vai:
- ✅ Solicitar sua senha de forma segura
- ✅ Testar a conexão
- ✅ Criar as tabelas necessárias
- ✅ Configurar os índices

### Opção 2: Configuração Manual

#### 1. Adicionar no arquivo `.env`

Adicione estas linhas no arquivo `.env`:

```env
# Supabase Database Configuration
SUPABASE_HOST=db.nywykslatlripxpiehfb.supabase.co
SUPABASE_PORT=5432
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=SUA_SENHA_AQUI

# Supabase URL e Service Role Key
SUPABASE_URL=https://nywykslatlripxpiehfb.supabase.co
SUPABASE_SERVICE_ROLE_KEY=SUA_SERVICE_ROLE_KEY_AQUI

# Database URL (para psycopg2 e outras libs)
DATABASE_URL=postgresql://postgres:SUA_SENHA_AQUI@db.nywykslatlripxpiehfb.supabase.co:5432/postgres
```

#### 2. Criar as Tabelas

Você tem duas opções:

**Opção A: Via Script Python**

```powershell
# Ativar ambiente virtual
.\agno_env\Scripts\Activate.ps1

# Executar setup
python setup_supabase.py
```

**Opção B: Via SQL Editor do Supabase**

1. Acesse: https://supabase.com/dashboard/project/nywykslatlripxpiehfb/editor/sql
2. Copie o conteúdo do arquivo `supabase_schema.sql`
3. Cole no SQL Editor
4. Clique em "Run"

## 📊 Tabelas que serão criadas

### 1. `aria_chunks` - Armazenamento de Conhecimento (RAG)
- Armazena textos e embeddings para busca semântica
- Suporta embedding de 1536 dimensões (OpenAI)
- Índices para busca híbrida (vetorial + texto)

### 2. `aria_sessions` - Sessões de Conversação
- Registra conversas com usuários
- Suporta múltiplos canais (WhatsApp, Web, etc.)
- Metadados flexíveis em JSONB

### 3. `aria_messages` - Mensagens Trocadas
- Histórico completo de mensagens
- Referencia sessões
- Roles: user, assistant, system

## 🔍 Como Obter a Service Role Key

1. Acesse: https://supabase.com/dashboard/project/nywykslatlripxpiehfb/settings/api
2. Procure por "Service Role" (secret)
3. Copie a chave (começa com `eyJ...`)
4. Adicione no `.env` na variável `SUPABASE_SERVICE_ROLE_KEY`

⚠️ **IMPORTANTE**: A Service Role Key tem acesso total ao banco. Mantenha-a em segredo!

## 🧪 Testar a Configuração

Após configurar, teste com:

```powershell
# Testar conexão
python -c "import psycopg2; conn = psycopg2.connect('SUA_CONNECTION_STRING'); print('✅ Conexão OK!')"

# Verificar tabelas
python setup_supabase.py
```

## 📡 Endpoints RAG

Com o Supabase configurado, você poderá usar:

- `POST /rag/query` - Buscar conhecimento
- RAG híbrido (vetorial + texto)
- Contexto enriquecido para respostas

## 🚀 Próximos Passos

1. ✅ Forneça a senha do banco de dados
2. ⏳ Execute `configurar_supabase.ps1`
3. ⏳ Verifique se as tabelas foram criadas
4. ⏳ Teste a API RAG
5. ⏳ Faça ingestão de documentos (FAQ, etc.)

## 🆘 Problemas Comuns

### "Conexão recusada"
- Verifique se o IP está na whitelist do Supabase
- Vá em Settings > Database > Connection pooling
- Adicione seu IP ou use "Allow all IPs" (apenas dev)

### "pgvector extension not found"
- Execute no SQL Editor: `CREATE EXTENSION IF NOT EXISTS vector;`
- Se não tiver permissão, entre em contato com suporte Supabase

### "RPC match failed: 404"
- Verifique se a função `match_aria_chunks` existe
- Execute o `supabase_schema.sql` completo

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs: `tail -f last_error.log`
2. Teste a conexão diretamente com psql
3. Consulte a documentação: https://supabase.com/docs

---

**Status:** ⏳ Aguardando senha do banco de dados

