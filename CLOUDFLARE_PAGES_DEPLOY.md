# Deploy na Cloudflare Pages

Esta é uma alternativa mais simples ao Cloudflare Workers, usando Cloudflare Pages Functions.

## Estrutura do Projeto

```
aria-endpoint/
├── functions/
│   └── api/
│       ├── assist-routing.js      # Endpoint principal
│       ├── healthz.js             # Health check
│       └── webhookassistrouting.js # Alias para compatibilidade
├── _headers                       # Configuração de CORS
├── _redirects                     # Redirecionamentos
└── package.json
```

## Deploy via GitHub

1. **Fazer push do código para GitHub**:
   ```bash
   git add .
   git commit -m "Add Cloudflare Pages configuration"
   git push origin main
   ```

2. **Conectar ao Cloudflare Pages**:
   - Acesse: <https://dash.cloudflare.com/pages>
   - Clique em "Create a project"
   - Conecte seu repositório GitHub
   - Configure:
     - **Framework preset**: None
     - **Build command**: (deixe vazio)
     - **Build output directory**: (deixe vazio)

3. **Configurar variáveis de ambiente**:
   - Na dashboard do Pages, vá em Settings > Environment variables
   - Adicione:
     - `FASTAPI_BEARER_TOKEN`: `dtransforma2026`
     - `OPENAI_API_KEY`: (sua chave da OpenAI)
     - `SUPABASE_URL`: (sua URL do Supabase)
     - `SUPABASE_SERVICE_ROLE_KEY`: (sua chave do Supabase)

## Deploy via Wrangler (alternativo)

```bash
# Instalar Pages CLI
npm install -g @cloudflare/pages-cli

# Fazer deploy
npx pages deploy
```

## URL Pública

Após o deploy, sua API estará disponível em:
- **URL Base**: `https://aria-endpoint.pages.dev` (ou seu domínio customizado)
- **Endpoints**:
  - `GET /api/healthz` - Health check
  - `POST /api/assist-routing` - Endpoint principal
  - `POST /api/webhookassistrouting` - Alias para compatibilidade

## Teste da API

```bash
# Health check
curl https://aria-endpoint.pages.dev/api/healthz

# Teste do endpoint principal
curl -X POST https://aria-endpoint.pages.dev/api/assist-routing \
  -H "Authorization: Bearer dtransforma2026" \
  -H "Content-Type: application/json" \
  -d '{"input": "quero enviar mensagens", "variables": {"lead_volumetria": "1500"}}'
```

## Vantagens do Cloudflare Pages

- ✅ Mais simples de configurar que Workers
- ✅ Não precisa de token com permissões especiais
- ✅ Deploy automático via GitHub
- ✅ Suporte nativo a CORS
- ✅ CDN global da Cloudflare
- ✅ HTTPS automático

## Próximos Passos

1. Fazer push do código para GitHub
2. Conectar ao Cloudflare Pages
3. Configurar variáveis de ambiente
4. Testar a API
5. Configurar domínio customizado (opcional)
