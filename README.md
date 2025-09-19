# ARIA — Agente de Relacionamento Inteligente da AR Online
> **Missão:** triagem e orientação de clientes via WhatsApp e chat web (Typebot), com rotações para n8n, FastAPI e OpenAI Assistants. Foco em **determinismo de decisões**, **segurança/LGPD** e **escalabilidade**.

---

## 🔎 Visão Geral
A ARIA é um orquestrador de atendimento multicanal. A conversa inicia no **Typebot**, segue para o **n8n** (controle de fluxo e integrações), passa pela **FastAPI** (lógica central/roteamento/assinaturas) e, quando necessário, utiliza **OpenAI Assistants** (threads + tools + retrieval) para FAQ/auxílio cognitivo.

### Macro-Arquitetura (validada)
* **Typebot** → interface conversacional inicial
* **n8n** → orquestração (recepção, roteamento, integrações externas)
* **FastAPI** → backend de roteamento, lógica central e segurança
* **OpenAI Assistants** → processamento inteligente, RAG e fallback de FAQs
* **Webhook principal n8n (routing):** `https://n8n-inovacao.ar-infra.com.br/webhook/assist/routing`
```mermaid
flowchart LR
  U[Usuário (WhatsApp/Web)] -->|mensagem| T(Typebot)
  T -->|payload JSON| N[n8n]
  N -->|chama| F(FastAPI)
  F -->|threads/runs| OA[OpenAI Assistants]
  OA -->|resposta| F
  F -->|reply_text + variáveis| N
  N -->|mensagem formatada| T
  T --> U
```

---

## ✅ Regras de Negócio (determinísticas)
> Decisões críticas **não** dependem apenas do LLM. Usar **Condition/Code** no n8n.

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
### 1) Entrada do Typebot → n8n

```json
{
  "channel": "typebot|whatsapp",
  "sender": "+55XXXXXXXXXX",
  "user_text": "mensagem do cliente",
  "thread_id": "abc123" // opcional: gerar se ausente
}
```

### 2) n8n → FastAPI (assinada)
```json
{
  "thread_id": "abc123",
  "lead_volumetria": 1500,
  "context": {"canal": "typebot"},
  "intent": "recebimento|triagem|faq",
  "user_text": "..."
}
```

### 3) FastAPI → n8n (resposta consolidada)
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
* Assinar chamadas **n8n → FastAPI** (AUTH\_TOKEN + HMAC, headers com timestamp/nonce)
* Registrar consentimento e finalidade quando coletar dados pessoais
* Logar **somente** metadados necessários (anonimizar PII nos logs)
* Versionar prompts e garantir **integridade** (hash das versões)
* Armazenar evidências de **autenticidade, integridade e validade jurídica** das comunicações

---

## 🚀 Quickstart (Dev)

### Requisitos
* Python 3.11+
* Docker + Docker Compose (opcional, recomendado)
* n8n acessível
* Credenciais OpenAI

### 1) Clone & .env
```bash
git clone https://github.com/lourealiza/aria-platform.git
cd aria-platform
cp .env.example .env
```

`.env` (exemplo)

```
AUTH_TOKEN=changeme
OPENAI_API_KEY=sk-...
OPENAI_ASSISTANT_ID=asst_...
VOL_THRESHOLD=1200
N8N_ROUTING_WEBHOOK=https://n8n-inovacao.ar-infra.com.br/webhook/assist/routing
ALLOWED_ORIGINS=*
```

### 2) Rodando com Docker
```bash
docker compose up --build
# ou
docker run -p 8000:8000 --env-file .env ghcr.io/aria/fastapi:latest
```

### 3) Healthcheck
```bash
curl -s http://localhost:8000/health
```

---

## 🧭 Endpoints (FastAPI)
* `GET /health` → status
* `POST /assist/routing` → entrada do n8n (roteamento/assinatura)
* `POST /assist/faq` → consulta Assistants (quando chamado diretamente)
* `POST /threads/create` → cria/normaliza `thread_id` (se necessário)

> Obs.: mantenha **idempotência** em `/assist/routing` usando `thread_id` + `nonce`.

---

## 🧪 Testes Rápidos (cURL)
### 1) Typebot (Preview)
* Start: `https://bot.automatizae.com.br/api/v1/typebots/<TYPEBOT_ID>/preview/startChat`
* Continue: `https://bot.automatizae.com.br/api/v1/sessions/<SESSION_ID>/continueChat`

```bash
# iniciar
curl -X POST \
  -H 'content-type: application/json' \
  -d '{"message":"Olá ARIA"}' \
  'https://bot.automatizae.com.br/api/v1/typebots/<TYPEBOT_ID>/preview/startChat'

# continuar
curl -X POST \
  -H 'content-type: application/json' \
  -d '{"message":"Quero enviar 2000 e-mails"}' \
  'https://bot.automatizae.com.br/api/v1/sessions/<SESSION_ID>/continueChat'
```

### 2) Rota n8n (routing)
```bash
curl -X POST \
  -H "content-type: application/json" \
  -H "x-auth: $AUTH_TOKEN" \
  -d '{
    "channel":"typebot",
    "sender":"+55...",
    "user_text":"Quero enviar 1500",
    "thread_id":"abc123"
  }' \
  "$N8N_ROUTING_WEBHOOK"
```

### 3) FastAPI direto (mock)
```bash
curl -X POST http://localhost:8000/assist/routing \
  -H "content-type: application/json" -H "x-auth: $AUTH_TOKEN" \
  -d '{"thread_id":"abc123","user_text":"FAQ: planos"}'
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
├─ n8n/                # fluxos exportados (.json)
├─ typebot/            # blocos, prompts e assets
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
* Métricas: tempo por etapa (Typebot→n8n, n8n→FastAPI, FastAPI→OpenAI)
* APM opcional (OTel)

---

## 🗺️ Roadmap (próximas frentes)
* Canais adicionais: **AR-Email**, **AR-SMS**, **AR-Voz**, **AR-Cartas**
* Integração CRM (VTiger) para criação automática de oportunidades
* API AR Online para disparos diretos (portal, API, SFTP, sufixo `@registra.email`)
* Áudio: upload → transcrição (n8n/FastAPI) → mesmo roteamento de texto
* Suite de **evaluations** para regressão de qualidade (baseline + casos críticos)

---

## 🤝 Contribuição
1. Crie uma branch: `feat/minha-feature`
2. Commits descritivos (Convencional)
3. Abra PR com **descrição do fluxo**, **variáveis usadas** e **screenshots** do n8n/Typebot

---

## 📄 Licença

Proprietário — AR Online. Uso interno.
