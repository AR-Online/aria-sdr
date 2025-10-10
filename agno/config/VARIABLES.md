# Mapeamento de Variáveis de Ambiente - ARIA-SDR

## Variáveis Principais (já configuradas)

### FastAPI / Autenticação
- `FASTAPI_BEARER_TOKEN` - Token de autenticação para a API
- `BEARER_TOKEN` - Token legado (fallback)
- `API_HOST` - Host da API (0.0.0.0)
- `API_PORT` - Porta da API (8000)
- `API_LOG_LEVEL` - Nível de log (info)

### OpenAI
- `OPENAI_API_KEY` - Chave da API OpenAI ✅ **JÁ CONFIGURADA**
- `ASSISTANT_ID` - ID do Assistant ✅ **JÁ CONFIGURADA**
- `ASSISTANT_TIMEOUT_SECONDS` - Timeout do Assistant (12)

### Supabase (RAG)
- `SUPABASE_URL` - URL do projeto Supabase ✅ **JÁ CONFIGURADA**
- `SUPABASE_SERVICE_ROLE_KEY` - Chave de serviço ✅ **JÁ CONFIGURADA**
- `EMBEDDING_MODEL` - Modelo de embedding (text-embedding-3-small)
- `EMBEDDING_DIM` - Dimensão do embedding (1536)

### RAG Client
- `RAG_ENABLE` - Habilitar RAG (true)
- `RAG_ENDPOINT` - Endpoint do RAG (http://127.0.0.1:8000/rag/query)
- `RAG_DEFAULT_SOURCE` - Fonte padrão (faq)

### Regras de Negócio
- `VOLUME_ALTO_LIMIAR` - Limite de volume alto (1200)

### Agno (novas variáveis)
- `AGNO_ROUTING_WEBHOOK` - Webhook do Agno
- `AGNO_API_BASE_URL` - URL base da API do Agno
- `AGNO_AUTH_TOKEN` - Token de autenticação do Agno
- `AGNO_BOT_ID` - ID do bot no Agno

### Cloudflare (já configurado)
- `CLOUDFLARE_API_TOKEN` - Token da API Cloudflare ✅ **CONFIGURADO**

## Como usar

1. **Copie o arquivo de exemplo:**
   ```bash
   cp config.env.example .env
   ```

2. **Configure apenas as variáveis do Agno:**
   ```bash
   # Adicione ao .env:
   AGNO_AUTH_TOKEN=seu_token_agno_aqui
   AGNO_BOT_ID=seu_bot_id_aqui
   ```

3. **Todas as outras variáveis já estão configuradas** com os valores que funcionavam no projeto original.

## Verificação

Para verificar se todas as variáveis estão sendo carregadas:

```bash
# Teste a API
curl -X GET http://localhost:8000/healthz

# Teste com autenticação
curl -X POST http://localhost:8000/assist/routing \
  -H "Authorization: Bearer $FASTAPI_BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_text": "teste"}'
```
