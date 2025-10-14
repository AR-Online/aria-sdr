# Deploy via GitHub + Cloudflare Pages

## 🚀 Instruções Rápidas

### 1. Fazer Push para GitHub

```bash
# Adicionar todos os arquivos
git add .

# Fazer commit
git commit -m "Add Cloudflare Pages proxy configuration"

# Fazer push
git push origin main
```

### 2. Conectar ao Cloudflare Pages

1. Acesse: <https://dash.cloudflare.com/pages>
2. Clique em **"Create a project"**
3. Conecte seu repositório GitHub
4. Configure:
   - **Framework preset**: `None`
   - **Build command**: (deixe vazio)
   - **Build output directory**: (deixe vazio)
   - **Root directory**: (deixe vazio)

### 3. Deploy Automático

Após conectar o repositório, o deploy será automático! 🎉

## 📋 Estrutura do Projeto

```
aria-endpoint/
├── functions/
│   └── api/
│       ├── assist-routing.js      # Proxy principal
│       ├── healthz.js             # Health check
│       └── webhookassistrouting.js # Alias para compatibilidade
├── _headers                       # Configuração de CORS
├── _redirects                     # Redirecionamentos
├── worker.js                      # Worker alternativo
├── wrangler.toml                  # Configuração Workers
└── package.json
```

## 🌐 URLs Públicas

Após o deploy, sua API estará disponível em:

- **URL Base**: `https://aria-endpoint.pages.dev`
- **Endpoints**:
  - `GET /api/healthz` - Health check
  - `POST /api/assist-routing` - Proxy para n8n
  - `POST /api/webhookassistrouting` - Alias para compatibilidade

## 🧪 Teste da API

```bash
# Health check
curl https://aria-endpoint.pages.dev/api/healthz

# Teste do proxy
curl -X POST https://aria-endpoint.pages.dev/api/assist-routing \
  -H "Content-Type: application/json" \
  -d '{"input": "quero enviar mensagens", "variables": {"lead_volumetria": "1500"}}'
```

## ⚙️ Como Funciona

O Cloudflare Pages Functions atua como um **proxy transparente**:

1. **Recebe** requisições na URL pública
2. **Redireciona** para `https://n8n-inovacao.ar-infra.com.br/webhook/assist/routing`
3. **Retorna** a resposta do n8n com CORS configurado

## 🔧 Vantagens

- ✅ **Deploy automático** via GitHub
- ✅ **CORS configurado** automaticamente
- ✅ **HTTPS automático**
- ✅ **CDN global** da Cloudflare
- ✅ **Sem necessidade de token** com permissões especiais
- ✅ **Proxy transparente** para o n8n

## 📝 Próximos Passos

1. **Fazer push** do código para GitHub
2. **Conectar** ao Cloudflare Pages
3. **Testar** a API
4. **Configurar domínio customizado** (opcional)

## 🆘 Troubleshooting

Se algo não funcionar:

1. Verifique se o repositório foi conectado corretamente
2. Confirme que o build foi bem-sucedido
3. Teste o endpoint `/api/healthz` primeiro
4. Verifique os logs no dashboard do Cloudflare Pages
