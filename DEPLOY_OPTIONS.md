# Opções de Deploy para ARIA Endpoint

## 🚀 Resumo das Opções

Você tem **3 opções** para hospedar sua API FastAPI:

### 1. Cloudflare Workers (Recomendado para APIs)

- **URL**: `https://aria-endpoint.seu-subdomain.workers.dev`
- **Prós**: Serverless, baixa latência, ideal para APIs
- **Contras**: Precisa de token com permissões especiais
- **Status**: ⚠️ Token atual não tem permissões necessárias

### 2. Cloudflare Pages (Mais Simples)

- **URL**: `https://aria-endpoint.pages.dev`
- **Prós**: Deploy via GitHub, mais simples, CORS automático
- **Contras**: Menos otimizado para APIs puras
- **Status**: ✅ Pronto para deploy

### 3. Servidor Local + Túnel (Desenvolvimento)

- **URL**: `https://seu-tunnel.ngrok.io` (ou similar)
- **Prós**: Ideal para desenvolvimento e testes
- **Contras**: Não é produção
- **Status**: ✅ Funcionando localmente

## 📋 Instruções Rápidas

### Opção 1: Cloudflare Workers

```bash
# 1. Criar token com permissões Workers
# 2. Configurar token
$env:CLOUDFLARE_API_TOKEN="seu_token_com_permissoes"

# 3. Deploy
npx wrangler deploy
```

### Opção 2: Cloudflare Pages

```bash
# 1. Fazer push para GitHub
git add .
git commit -m "Add Cloudflare Pages config"
git push origin main

# 2. Conectar repositório ao Cloudflare Pages
# 3. Configurar variáveis de ambiente
# 4. Deploy automático!
```

### Opção 3: Túnel Local

```bash
# 1. Instalar ngrok
npm install -g ngrok

# 2. Rodar API local
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 3. Criar túnel
ngrok http 8000
```

## 🎯 Recomendação

Para **produção**, recomendo a **Cloudflare Pages** porque:

- É mais simples de configurar
- Não precisa de token com permissões especiais
- Deploy automático via GitHub
- CDN global da Cloudflare
- HTTPS automático

## 📞 Próximos Passos

1. **Escolha uma opção** acima
2. **Siga as instruções** específicas
3. **Teste a API** com os endpoints fornecidos
4. **Configure domínio customizado** (opcional)

## 🔗 URLs dos Endpoints

Independente da opção escolhida, os endpoints serão:

- `GET /healthz` - Health check
- `POST /assist/routing` - Endpoint principal
- `POST /webhookassistrouting` - Alias para compatibilidade
- `POST /rag/query` - Endpoint RAG (simplificado)

## 🧪 Teste Rápido

```bash
# Health check
curl https://sua-url-aqui/healthz

# Teste completo
curl -X POST https://sua-url-aqui/assist/routing \
  -H "Authorization: Bearer dtransforma2026" \
  -H "Content-Type: application/json" \
  -d '{"input": "quero enviar mensagens", "variables": {"lead_volumetria": "1500"}}'
```
