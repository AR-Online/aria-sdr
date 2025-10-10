# Agno Integration

Este diretório contém as configurações e integrações específicas do Agno para o ARIA-SDR.

## Estrutura

- `config/` - Configurações do Agno
- `flows/` - Fluxos de conversação exportados
- `webhooks/` - Configurações de webhooks
- `templates/` - Templates de mensagens

## Configuração

O Agno substitui o Typebot e n8n na arquitetura do ARIA-SDR, fornecendo:

1. **Interface conversacional inteligente** - Substitui o Typebot
2. **Orquestração de fluxos** - Substitui o n8n
3. **Integração direta com FastAPI** - Comunicação simplificada

## Webhook Principal

```
https://api.ar-online.com.br/webhook/assist/routing
```

## Payload de Entrada

```json
{
  "channel": "agno|whatsapp",
  "sender": "+55XXXXXXXXXX",
  "user_text": "mensagem do cliente",
  "thread_id": "abc123"
}
```

## Payload de Resposta

```json
{
  "thread_id": "abc123",
  "volume_class": "alto",
  "fluxo_path": "agendamento",
  "reply_text": "Posso agendar uma demonstração?",
  "meta": {"assistant_used": true}
}
```
