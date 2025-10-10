# Agno Webhook Configuration

## Webhook Principal
- **URL**: `https://agno.ar-infra.com.br/webhook/assist/routing`
- **Método**: POST
- **Autenticação**: Bearer Token

## Payload de Entrada (Agno → FastAPI)

```json
{
  "channel": "agno|whatsapp",
  "sender": "+55XXXXXXXXXX",
  "user_text": "mensagem do cliente",
  "thread_id": "abc123",
  "session_id": "sess_xyz",
  "metadata": {
    "source": "whatsapp",
    "timestamp": "2025-01-10T17:45:00Z"
  }
}
```

## Payload de Resposta (FastAPI → Agno)

```json
{
  "thread_id": "abc123",
  "volume_class": "alto",
  "fluxo_path": "agendamento",
  "reply_text": "Posso agendar uma demonstração?",
  "next_action": "schedule",
  "variables": {
    "volume_num": "1500",
    "lead_volumetria": "1500",
    "volume_alto": "true",
    "volume_class": "alto"
  },
  "meta": {
    "assistant_used": true,
    "rag_context": "contexto encontrado...",
    "confidence": 0.85
  }
}
```

## Headers de Autenticação

```
Authorization: Bearer <AGNO_AUTH_TOKEN>
Content-Type: application/json
X-Thread-Id: <thread_id>
X-Trace-Id: <trace_id>
```

## Configuração de Retry

- **Tentativas**: 3
- **Backoff**: Exponencial (0.3s, 0.6s, 1.2s)
- **Timeout**: 30 segundos
- **Status codes**: 429, 500, 502, 503, 504
