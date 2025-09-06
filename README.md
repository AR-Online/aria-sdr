# aria-platform
Endpoint FastAPI da ARIA para roteamento Typebot → n8n → OpenAI (Assistants). Regras de volumetria, prompts e integrações.

# ARIA — Endpoint FastAPI

Webhook/endpoint FastAPI para roteamento **Typebot → n8n → OpenAI (Assistants)**.

## Arquitetura (resumo)
- Typebot → **n8n** (webhook público, sem segredo)
- n8n → **FastAPI** (assina a chamada, adiciona AUTH_TOKEN)
- FastAPI → **OpenAI Assistants** (threads/runs + tool-calls)
- Regras de negócio: **volumetria** (envio alto/baixo), prompts de **recebimento** e **triagem**
