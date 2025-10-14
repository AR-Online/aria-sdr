# ARIA-SDR — Agente de Relacionamento Inteligente da AR Online
> **Missão:** triagem e orientação de clientes via WhatsApp e chat web (Agno), com integração direta ao FastAPI e OpenAI Assistants. Foco em **determinismo de decisões**, **segurança/LGPD** e **escalabilidade**.

---

## 🔎 Visão Geral
A ARIA-SDR é um orquestrador de atendimento multicanal modernizado. A conversa inicia no **Agno** (interface conversacional inteligente), integra diretamente com a **FastAPI** (lógica central/roteamento/assinaturas) e utiliza **OpenAI Assistants** (threads + tools + retrieval) para FAQ/auxílio cognitivo.

<<<<<<< HEAD
### Macro-Arquitetura (Agno-Centric)
* **Agno** → interface conversacional inteligente e orquestração principal
* **FastAPI** → backend de roteamento, lógica central e segurança
* **OpenAI Assistants** → processamento inteligente, RAG e fallback de FAQs
* **WhatsApp** → canal de comunicação via Mindchat
* **Cloudflare** → segurança e performance
* **Webhook principal Agno:** `https://api.ar-online.com.br/webhook/assist/routing`
```mermaid
flowchart LR
  U[Usuário WhatsApp] -->|mensagem| M[Mindchat]
  M -->|webhook| A(Agno)
  A -->|payload JSON| F(FastAPI)
  F -->|threads/runs| OA[OpenAI Assistants]
  OA -->|resposta| F
  F -->|reply_text + variáveis| A
  A -->|mensagem formatada| M
  M -->|WhatsApp| U
  
  CF[Cloudflare] -.->|segurança| F
  SB[Supabase] -.->|RAG| F
```

---

## ✅ Regras de Negócio (determinísticas)
> Decisões críticas **não** dependem apenas do LLM. Usar **Condition/Code** no Agno.

**Variáveis padronizadas**

* `lead_volumetria`: número informado pelo remetente
* `volume_class`: "alto" | "baixo"
* `volume_alto`: boolean (ex.: `lead_volumetria >= 1200`)
* `fluxo_path`: "recebimento" | "triagem" | "faq" | "agendamento" | "loja"
* `thread_id`: id curto por conversa (criar se ausente)
* `reply_text`: texto final a ser enviado ao canal

**Classificação de volumetria**

* **Threshold padrão:** `1200`
* **Baixo volume** → CTA **Loja**
* **Alto volume** → CTA **Agendamento** (abre oportunidade no CRM / VTiger)

**Fallback (FAQ)**

1. Busca em documentos internos (RAG / file\_search)
2. Se não houver contexto suficiente, aciona Assistant com prompt institucional

---

## 🧩 Contratos de Payload
### 1) Entrada do Agno → FastAPI

```json
{
  "channel": "agno|whatsapp",
  "sender": "+55XXXXXXXXXX",
  "user_text": "mensagem do cliente",
  "thread_id": "abc123" // opcional: gerar se ausente
}
```

### 2) Agno → FastAPI (assinada)
```json
{
  "thread_id": "abc123",
  "lead_volumetria": 1500,
  "context": {"canal": "agno"},
  "intent": "recebimento|triagem|faq",
  "user_text": "..."
}
```

### 3) FastAPI → Agno (resposta consolidada)
```json
{
  "thread_id": "abc123",
  "volume_class": "alto",
  "fluxo_path": "agendamento",
  "reply_text": "Posso agendar uma demonstração?",
  "meta": {"assistant_used": true}
}
```

---

## 🔐 Segurança & Conformidade (LGPD / ICP-Brasil)
* Assinar chamadas **Agno → FastAPI** (AUTH\_TOKEN + HMAC, headers com timestamp/nonce)
* Registrar consentimento e finalidade quando coletar dados pessoais
* Logar **somente** metadados necessários (anonimizar PII nos logs)
* Versionar prompts e garantir **integridade** (hash das versões)
* Armazenar evidências de **autenticidade, integridade e validade jurídica** das comunicações

---

## 🚀 Quickstart (Dev)

### Requisitos
* Python 3.10+
* Docker + Docker Compose (opcional, recomendado)
* Agno acessível
* Credenciais OpenAI

### 1) Clone & .env
```bash
git clone https://github.com/AR-Online/ARIA-SDR.git
cd ARIA-SDR
cp config.env.example .env

# Verificar configuração
python check_env.py

# Testar integração WhatsApp
python test_whatsapp_integration.py
```

`.env` (exemplo - **use as mesmas variáveis do projeto original**)

```
# --- FastAPI / Auth ---
API_HOST=0.0.0.0
API_PORT=8000
API_LOG_LEVEL=info
FASTAPI_BEARER_TOKEN=dtransforma
BEARER_TOKEN=dtransforma

# --- OpenAI (já configurado) ---
OPENAI_API_KEY=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
ASSISTANT_ID=asst_Y9PUGUtEqgQWhg1WSkgPPzt6
ASSISTANT_TIMEOUT_SECONDS=12

# --- Supabase (já configurado) ---
SUPABASE_URL=https://hnagqhgfskhmqweeqvts.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhuYWdxaGdmc2tobXF3ZWVxdnRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDk2MzYyNywiZXhwIjoyMDcwNTM5NjI3fQ.t_bAT6CwPbDp8BH_3NeFtTRSw1WLhS4jorsyh6-MZiE
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536

# --- RAG client ---
RAG_ENABLE=true
RAG_ENDPOINT=http://127.0.0.1:8000/rag/query
RAG_DEFAULT_SOURCE=faq

# --- Business rules ---
VOLUME_ALTO_LIMIAR=1200

# --- Agno Integration (configure apenas estas) ---
AGNO_ROUTING_WEBHOOK=https://agno.ar-infra.com.br/webhook/assist/routing
AGNO_API_BASE_URL=https://agno.ar-infra.com.br/api/v1
AGNO_AUTH_TOKEN=seu_token_agno_aqui
AGNO_BOT_ID=seu_bot_id_aqui

# --- Cloudflare Integration (já configurado) ---
CLOUDFLARE_API_TOKEN=JV_d0yng1HI5vcxJaebMpiuoC04gRifT3SbBhT7U

# --- Mindchat Integration (já configurado) ---
MINDCHAT_API_TOKEN=c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58
MINDCHAT_API_BASE_URL=https://api-aronline.mindchatapp.com.br
MINDCHAT_API_DOCS=https://api-aronline.mindchatapp.com.br/api-docs/
```

**💡 Importante:** Todas as variáveis principais (OpenAI, Supabase, Cloudflare, Mindchat, etc.) já estão configuradas com os valores que funcionavam no projeto original. Você só precisa configurar `AGNO_AUTH_TOKEN` e `AGNO_BOT_ID`.

### 2) Rodando com Docker
```bash
docker compose up --build
# ou
docker run -p 8000:8000 --env-file .env ghcr.io/aria/fastapi:latest
```

### 3) Verificar Configuração
```bash
# Verificar se todas as variáveis estão configuradas
python check_env.py

# Healthcheck
curl -s http://localhost:8000/healthz
```

---

## 🧭 Endpoints (FastAPI)
* `GET /healthz` → status
* `POST /assist/routing` → entrada do Agno (roteamento/assinatura)
* `POST /assist/faq` → consulta Assistants (quando chamado diretamente)
* `POST /threads/create` → cria/normaliza `thread_id` (se necessário)
* `POST /whatsapp/webhook` → webhook para mensagens WhatsApp via Mindchat
* `GET /whatsapp/status` → status da integração WhatsApp
* `GET /cloudflare/metrics` → métricas do Cloudflare
* `POST /cloudflare/setup` → configura proteção Cloudflare
* `POST /cloudflare/purge-cache` → limpa cache do Cloudflare

> Obs.: mantenha **idempotência** em `/assist/routing` usando `thread_id` + `nonce`.

---

## 🧪 Testes Rápidos (cURL)
### 1) Agno (Preview)
* Start: `https://agno.ar-infra.com.br/api/v1/agno/<AGNO_ID>/preview/startChat`
* Continue: `https://agno.ar-infra.com.br/api/v1/sessions/<SESSION_ID>/continueChat`

```bash
# iniciar
curl -X POST \
  -H 'content-type: application/json' \
  -d '{"message":"Olá ARIA"}' \
  'https://agno.ar-infra.com.br/api/v1/agno/<AGNO_ID>/preview/startChat'

# continuar
curl -X POST \
  -H 'content-type: application/json' \
  -d '{"message":"Quero enviar 2000 e-mails"}' \
  'https://agno.ar-infra.com.br/api/v1/sessions/<SESSION_ID>/continueChat'
```

### 2) Rota Agno (routing)
```bash
curl -X POST \
  -H "content-type: application/json" \
  -H "x-auth: $AUTH_TOKEN" \
  -d '{
    "channel":"agno",
    "sender":"+55...",
    "user_text":"Quero enviar 1500",
    "thread_id":"abc123"
  }' \
  "$AGNO_ROUTING_WEBHOOK"
```

### 3) WhatsApp Integration
```bash
# Testar status da integração WhatsApp
curl -X GET http://localhost:8000/whatsapp/status \
  -H "Authorization: Bearer $FASTAPI_BEARER_TOKEN"

# Testar webhook WhatsApp (simulação)
curl -X POST http://localhost:8000/whatsapp/webhook \
  -H "Authorization: Bearer $FASTAPI_BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+5516997918658",
    "to": "+5516997918658",
    "message": "Olá ARIA!",
    "timestamp": "2025-10-10T14:34:00Z",
    "id": "test_msg_001",
    "type": "text"
  }'
```

### 4) Cloudflare (métricas e configuração)
```bash
# Obter métricas do Cloudflare
curl -X GET http://localhost:8000/cloudflare/metrics \
  -H "Authorization: Bearer $FASTAPI_BEARER_TOKEN"

# Configurar proteção Cloudflare
curl -X POST http://localhost:8000/cloudflare/setup \
  -H "Authorization: Bearer $FASTAPI_BEARER_TOKEN"

# Limpar cache do Cloudflare
curl -X POST http://localhost:8000/cloudflare/purge-cache \
  -H "Authorization: Bearer $FASTAPI_BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '["https://api.ar-online.com.br/static/style.css"]'
```

---

## 🧱 Organização do Repositório

```
aria-platform/
├─ fastapi/            # app, routers, services, clients (openai)
│  ├─ main.py
│  ├─ routers/
│  ├─ services/
│  ├─ tests/
│  └─ pyproject.toml
├─ agno/               # configurações e integrações do Agno
├─ prompts/            # versões de prompts (hash + changelog)
├─ docs/               # README, diagramas (.drawio / .md)
└─ docker/
```

---

## 🧠 Prompts & Threads
* **Idioma padrão:** pt-BR; tom humano, cordial e objetivo
* **Threading:** se **não existir** `thread_id` na entrada, gerar id curto (ex.: base36/8)
* **Contexto priorizado:** quando houver `CONTEXTO:` no prompt, **use somente** esse conteúdo
* **RAG:** recuperar de bases internas **antes** de consultar o LLM

---

## 📈 Observabilidade
* Logs estruturados (JSON) com `thread_id`, `step`, `latency_ms`
* Métricas: tempo por etapa (Agno→FastAPI, FastAPI→OpenAI)
* APM opcional (OTel)

---

## 🗺️ Roadmap (próximas frentes)
* Canais adicionais: **AR-Email**, **AR-SMS**, **AR-Voz**, **AR-Cartas**
* Integração CRM (VTiger) para criação automática de oportunidades
* API AR Online para disparos diretos (portal, API, SFTP, sufixo `@registra.email`)
* Áudio: upload → transcrição (Agno/FastAPI) → mesmo roteamento de texto
* Suite de **evaluations** para regressão de qualidade (baseline + casos críticos)

---

## 🤝 Contribuição
1. Crie uma branch: `feat/minha-feature`
2. Commits descritivos (Convencional)
3. Abra PR com **descrição do fluxo**, **variáveis usadas** e **screenshots** do Agno

---

## 📄 Licença

Proprietário — AR Online. Uso interno.
=======
## Arquitetura (resumo)

- Typebot → **n8n** (webhook público, sem segredo)
- n8n → **FastAPI** (assina a chamada, adiciona AUTH_TOKEN)
- FastAPI → **OpenAI Assistants** (threads/runs + tool-calls)
- Regras de negócio: **volumetria** (envio alto/baixo), prompts de **recebimento** e **triagem**
>>>>>>> origin/feat/thread-id-routing-logs
