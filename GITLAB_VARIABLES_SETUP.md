# Configuração GitLab CI/CD - Variáveis de Ambiente ARIA-SDR

## Variáveis Críticas que Precisam ser Configuradas no GitLab

### 1. Variáveis do Agno (BLOQUEADORES)
```bash
# Estas variáveis são OBRIGATÓRIAS para o funcionamento do sistema Agno
AGNO_AUTH_TOKEN=seu_token_agno_aqui
AGNO_BOT_ID=seu_bot_id_agno_aqui
```

### 2. Como Configurar no GitLab

#### Opção 1: Via Interface Web
1. Acesse: https://gitlab.com/lourealiza/aria-sdr/-/settings/ci_cd
2. Expanda a seção "Variables"
3. Adicione as seguintes variáveis:

| Key | Value | Type | Environment | Protected | Masked |
|-----|-------|------|-------------|-----------|--------|
| `AGNO_AUTH_TOKEN` | `seu_token_real_aqui` | Variable | All | ✅ | ✅ |
| `AGNO_BOT_ID` | `seu_bot_id_real_aqui` | Variable | All | ✅ | ❌ |

#### Opção 2: Via GitLab CLI
```bash
# Instalar GitLab CLI
glab auth login

# Configurar variáveis
glab variable set AGNO_AUTH_TOKEN "seu_token_real_aqui" --masked
glab variable set AGNO_BOT_ID "seu_bot_id_real_aqui" --protected
```

### 3. Variáveis Já Configuradas (Não Precisam Alteração)

Estas variáveis já estão funcionando e não precisam ser alteradas:

```bash
# FastAPI
FASTAPI_BEARER_TOKEN=dtransforma2026
BEARER_TOKEN=dtransforma

# OpenAI
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
ASSISTANT_ID=asst_your-assistant-id-here

# Supabase
SUPABASE_URL=https://hnagqhgfskhmqweeqvts.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Cloudflare
CLOUDFLARE_API_TOKEN=JV_d0yng1HI5vcxJaebMpiuoC04gRifT3SbBhT7U

# Mindchat
MINDCHAT_API_TOKEN=c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58
MINDCHAT_API_BASE_URL=https://api-aronline.mindchatapp.com.br
```

### 4. Teste da Configuração

Após configurar as variáveis, teste com:

```bash
# Teste local
curl -X GET http://localhost:8000/healthz

# Teste de autenticação
curl -X POST http://localhost:8000/assist/routing \
  -H "Authorization: Bearer $FASTAPI_BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_text": "teste"}'
```

### 5. Pipeline GitLab CI/CD

O arquivo `.gitlab-ci.yml` já está configurado para usar essas variáveis:

```yaml
variables:
  AGNO_AUTH_TOKEN: $AGNO_AUTH_TOKEN
  AGNO_BOT_ID: $AGNO_BOT_ID
  # ... outras variáveis
```

### 6. Próximos Passos

1. ✅ Configurar `AGNO_AUTH_TOKEN` e `AGNO_BOT_ID` no GitLab
2. ✅ Testar pipeline CI/CD
3. ✅ Verificar logs de deploy
4. ✅ Validar funcionamento do sistema Agno

### 7. Troubleshooting

#### Problema: "AGNO_AUTH_TOKEN not found"
- Verificar se a variável está configurada no GitLab
- Verificar se está marcada como "Protected" e "Masked"
- Verificar se o valor não está vazio

#### Problema: "AGNO_BOT_ID not found"
- Verificar se a variável está configurada no GitLab
- Verificar se está marcada como "Protected"
- Verificar se o valor não está vazio

#### Problema: Pipeline falha
- Verificar logs do pipeline
- Verificar se todas as variáveis estão configuradas
- Verificar conectividade com serviços externos
