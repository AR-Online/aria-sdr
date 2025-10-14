# 🚀 Deploy Simples - Cloudflare Pages

## ✅ Solução Simplificada

Removi todas as configurações complexas que estavam causando problemas. Agora é só:

### 1. Fazer Push para GitHub

```bash
git add .
git commit -m "Simplify Cloudflare Pages configuration"
git push origin main
```

### 2. Conectar ao Cloudflare Pages

1. **Acesse**: https://dash.cloudflare.com/pages
2. **Clique em**: "Create a project"
3. **Conecte** seu repositório GitHub
4. **Configure**:
   - **Framework preset**: `None`
   - **Build command**: (deixe vazio)
   - **Build output directory**: (deixe vazio)
   - **Root directory**: (deixe vazio)

### 3. Deploy Automático! 🎉

## 📋 Estrutura Final

```
aria-endpoint/
├── functions/
│   └── api/
│       ├── assist-routing.js       # Proxy principal
│       ├── healthz.js              # Health check
│       └── webhookassistrouting.js # Alias
├── _redirects                      # Redirecionamentos
└── package.json                    # Configuração mínima
```

## 🌐 URLs Públicas

Após o deploy:

- **URL Base**: `https://aria-endpoint.pages.dev`
- **Endpoints**:
  - `GET /api/healthz` - Health check
  - `POST /api/assist-routing` - Proxy para n8n
  - `POST /api/webhookassistrouting` - Alias

## 🧪 Teste

```bash
# Health check
curl https://aria-endpoint.pages.dev/api/healthz

# Teste do proxy
curl -X POST https://aria-endpoint.pages.dev/api/assist-routing \
  -H "Content-Type: application/json" \
  -d '{"input": "quero enviar mensagens", "variables": {"lead_volumetria": "1500"}}'
```

## ⚙️ Como Funciona

```
Cliente → Cloudflare Pages → n8n Webhook → Resposta
```

1. **Cliente** faz requisição para `https://aria-endpoint.pages.dev/api/assist-routing`
2. **Cloudflare Pages** executa a function `functions/api/assist-routing.js`
3. **Function** redireciona para `https://n8n-inovacao.ar-infra.com.br/webhook/assist/routing`
4. **n8n** processa e retorna resposta
5. **Cloudflare** retorna resposta com CORS configurado

## 🔧 Vantagens

- ✅ **Configuração mínima** - sem arquivos complexos
- ✅ **Deploy automático** via GitHub
- ✅ **CORS automático**
- ✅ **HTTPS automático**
- ✅ **CDN global** da Cloudflare
- ✅ **Sem dependências** externas

## 🆘 Se Ainda Não Funcionar

1. **Delete o projeto** no Cloudflare Pages
2. **Crie um novo projeto**
3. **Conecte o repositório** novamente
4. **Configure como `None`** framework
5. **Deploy automático** funcionará!

---

**Agora está 100% simplificado!** 🚀
