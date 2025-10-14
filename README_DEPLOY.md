# 🚀 Deploy da API ARIA - Opções Disponíveis

## 📋 Resumo

Sua API FastAPI está configurada para funcionar como um **proxy transparente** que redireciona requisições para o webhook do n8n: `https://n8n-inovacao.ar-infra.com.br/webhook/assist/routing`

## 🎯 Opções de Deploy

### 1. 🌟 **Cloudflare Pages (RECOMENDADO)**

- **URL**: `https://aria-endpoint.pages.dev`
- **Status**: ✅ Pronto para deploy
- **Vantagens**: Deploy automático via GitHub, sem token especial

**Como fazer:**

```bash
# 1. Push para GitHub
git add .
git commit -m "Add Cloudflare Pages proxy"
git push origin main

# 2. Conectar ao Cloudflare Pages
# Acesse: https://dash.cloudflare.com/pages
# Conecte seu repositório
# Deploy automático! 🎉
```

### 2. ⚡ **Cloudflare Workers**

- **URL**: `https://aria-endpoint.seu-subdomain.workers.dev`
- **Status**: ⚠️ Precisa de token com permissões Workers
- **Vantagens**: Serverless, baixa latência

**Como fazer:**

```bash
# 1. Criar token com permissões Workers
# 2. Configurar token
$env:CLOUDFLARE_API_TOKEN="seu_token_com_permissoes"

# 3. Deploy
npx wrangler deploy
```

### 3. 🏠 **Servidor Local + Túnel**

- **URL**: `https://seu-tunnel.ngrok.io`
- **Status**: ✅ Funcionando localmente
- **Vantagens**: Ideal para desenvolvimento

**Como fazer:**

```bash
# 1. Instalar ngrok
npm install -g ngrok

# 2. Rodar API local
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 3. Criar túnel
ngrok http 8000
```

## 🔗 Endpoints Disponíveis

Independente da opção escolhida:

- `GET /healthz` - Health check
- `POST /assist/routing` - Endpoint principal (proxy para n8n)
- `POST /webhookassistrouting` - Alias para compatibilidade

## 🧪 Teste Rápido

```bash
# Health check
curl https://sua-url-aqui/healthz

# Teste do proxy
curl -X POST https://sua-url-aqui/assist/routing \
  -H "Content-Type: application/json" \
  -d '{"input": "quero enviar mensagens", "variables": {"lead_volumetria": "1500"}}'
```

## ⚙️ Como Funciona

```
Cliente → Cloudflare (URL Pública) → n8n Webhook → Resposta
```

1. **Cliente** faz requisição para URL pública
2. **Cloudflare** recebe e redireciona para n8n
3. **n8n** processa e retorna resposta
4. **Cloudflare** retorna resposta com CORS configurado

## 🎯 Recomendação Final

**Use Cloudflare Pages** porque:

- ✅ Mais simples de configurar
- ✅ Deploy automático via GitHub
- ✅ Não precisa de token especial
- ✅ CDN global da Cloudflare
- ✅ HTTPS automático

## 📞 Próximos Passos

1. **Escolha Cloudflare Pages** (recomendado)
2. **Faça push para GitHub**
3. **Conecte ao Cloudflare Pages**
4. **Teste a API**
5. **Configure domínio customizado** (opcional)

---

**Sua API estará pronta em minutos!** 🚀
