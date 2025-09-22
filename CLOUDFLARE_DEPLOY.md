# Deploy na Cloudflare Workers

## Configuração do Token

O token atual não tem as permissões necessárias para Workers. Você precisa criar um novo token com as seguintes permissões:

1. Acesse: https://dash.cloudflare.com/profile/api-tokens
2. Clique em "Create Token"
3. Use o template "Custom token"
4. Configure as permissões:
   - **Account** - `Cloudflare Workers:Edit`
   - **Account** - `Account Settings:Read`
   - **Zone** - `Zone:Read` (se necessário)

## Deploy

Após configurar o token com as permissões corretas:

```bash
# Configurar o token
$env:CLOUDFLARE_API_TOKEN="seu_novo_token_aqui"

# Fazer o deploy
npx wrangler deploy
```

## URL Pública

Após o deploy bem-sucedido, sua API estará disponível em:

- **URL Principal**: `https://aria-endpoint.seu-subdomain.workers.dev`
- **Endpoints**:
  - `GET /healthz` - Health check
  - `POST /assist/routing` - Endpoint principal de roteamento
  - `POST /webhookassistrouting` - Alias para compatibilidade
  - `POST /rag/query` - Endpoint RAG (simplificado)

## Teste da API

```bash
# Health check
curl https://aria-endpoint.seu-subdomain.workers.dev/healthz

# Teste do endpoint principal
curl -X POST https://aria-endpoint.seu-subdomain.workers.dev/assist/routing \
  -H "Authorization: Bearer dtransforma2026" \
  -H "Content-Type: application/json" \
  -d '{"input": "quero enviar mensagens", "variables": {"lead_volumetria": "1500"}}'
```

## Configuração de Variáveis de Ambiente

Para configurar as variáveis de ambiente no Worker:

```bash
# Configurar token de autenticação
npx wrangler secret put FASTAPI_BEARER_TOKEN

# Configurar chave da OpenAI
npx wrangler secret put OPENAI_API_KEY

# Configurar Supabase
npx wrangler secret put SUPABASE_URL
npx wrangler secret put SUPABASE_SERVICE_ROLE_KEY

# Configurar Assistant ID
npx wrangler secret put ASSISTANT_ID
```

## Alternativa: Cloudflare Pages

Se preferir usar Cloudflare Pages (mais simples), você pode:

1. Fazer push do código para um repositório GitHub
2. Conectar o repositório ao Cloudflare Pages
3. Configurar o build command como `npm run build`
4. A API estará disponível em `https://aria-endpoint.pages.dev`
