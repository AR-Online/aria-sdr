# 🔧 Correção do Deploy Cloudflare Pages

## ❌ Problema Identificado

O Cloudflare Pages está tentando executar `npx wrangler deploy` (comando para Workers) em vez de usar Pages Functions.

## ✅ Solução

### 1. Configuração Corrigida

Criei os arquivos de configuração corretos:

- `functions.json` - Configuração das Functions
- `pages.toml` - Configuração específica do Pages
- `functions/_middleware.js` - Middleware global
- `package.json` - Configuração correta para Pages

### 2. Fazer Push das Correções

```bash
# Adicionar as correções
git add .

# Fazer commit
git commit -m "Fix Cloudflare Pages configuration"

# Fazer push
git push origin main
```

### 3. Reconfigurar no Cloudflare Pages

1. **Acesse**: <https://dash.cloudflare.com/pages>
2. **Vá em**: Settings > Builds & deployments
3. **Configure**:
   - **Framework preset**: `None`
   - **Build command**: (deixe vazio)
   - **Build output directory**: (deixe vazio)
   - **Root directory**: (deixe vazio)

### 4. Deploy Manual (Alternativa)

Se ainda não funcionar, faça deploy manual:

```bash
# Instalar Pages CLI
npm install -g @cloudflare/pages-cli

# Fazer deploy manual
npx pages deploy
```

## 🎯 Estrutura Correta

```
aria-endpoint/
├── functions/
│   ├── _middleware.js              # Middleware global
│   └── api/
│       ├── assist-routing.js       # Proxy principal
│       ├── healthz.js              # Health check
│       └── webhookassistrouting.js # Alias
├── functions.json                  # Configuração Functions
├── pages.toml                      # Configuração Pages
├── _redirects                      # Redirecionamentos
└── package.json                    # Configuração correta
```

## 🧪 Teste Após Correção

```bash
# Health check
curl https://aria-endpoint.pages.dev/api/healthz

# Teste do proxy
curl -X POST https://aria-endpoint.pages.dev/api/assist-routing \
  -H "Content-Type: application/json" \
  -d '{"input": "quero enviar mensagens", "variables": {"lead_volumetria": "1500"}}'
```

## 🔍 Verificação

Após o deploy, verifique:

1. ✅ Build bem-sucedido (sem erros de wrangler)
2. ✅ Functions carregadas corretamente
3. ✅ Endpoints respondendo
4. ✅ Proxy funcionando

## 🆘 Se Ainda Não Funcionar

1. **Delete o projeto** no Cloudflare Pages
2. **Crie um novo projeto**
3. **Conecte o repositório** novamente
4. **Configure** como `None` framework
5. **Deploy automático** funcionará!

---

**A correção está pronta!** 🚀
