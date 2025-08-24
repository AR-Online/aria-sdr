# aria-platform
Endpoint FastAPI da ARIA para roteamento Typebot → n8n → OpenAI (Assistants). Regras de volumetria, prompts e integrações.

# ARIA — Endpoint FastAPI

Webhook/endpoint FastAPI para roteamento **Typebot → n8n → OpenAI (Assistants)**.

## Arquitetura (resumo)
- Typebot → **n8n** (webhook público, sem segredo)
- n8n → **FastAPI** (assina a chamada, adiciona AUTH_TOKEN)
- FastAPI → **OpenAI Assistants** (threads/runs + tool-calls)
- Regras de negócio: **volumetria** (envio alto/baixo), prompts de **recebimento** e **triagem**

## Como rodar local
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r api/requirements.txt
copy .env.example .env          # editar variáveis
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
