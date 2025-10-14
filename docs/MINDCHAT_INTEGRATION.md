# Integração Mindchat para ARIA-SDR

## Visão Geral

A integração com Mindchat permite que a ARIA-SDR receba e processe mensagens do WhatsApp em tempo real, utilizando RAG (Retrieval Augmented Generation) para fornecer respostas inteligentes e roteamento automático para diferentes fluxos de atendimento.

## Arquitetura da Integração

```
WhatsApp → Mindchat → ARIA-SDR → RAG/Agno → Resposta → Mindchat → WhatsApp
```

### Componentes Principais

1. **Webhook de Recebimento**: Recebe mensagens do WhatsApp via Mindchat
2. **Processamento RAG**: Analisa mensagens usando base de conhecimento
3. **Roteamento Inteligente**: Direciona para FAQ, agendamento ou vendas
4. **Envio de Respostas**: Envia respostas via API do Mindchat
5. **Monitoramento**: Acompanha status de entrega e leitura

## Configuração

### Variáveis de Ambiente

```bash
# Mindchat API Configuration
MINDCHAT_API_TOKEN=your_mindchat_api_token
MINDCHAT_API_BASE_URL=https://api-aronline.mindchat.com
MINDCHAT_API_DOCS=https://docs.mindchat.com

# Webhook Security
MINDCHAT_WEBHOOK_SECRET=your_webhook_secret
MINDCHAT_VERIFY_TOKEN=aria_verify_token

# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_WEBHOOK_URL=https://api.ar-online.com.br/webhook/mindchat/whatsapp
WHATSAPP_VERIFY_TOKEN=your_verify_token

# ARIA Configuration
ARIA_API_BASE_URL=https://api.ar-online.com.br
FASTAPI_BEARER_TOKEN=dtransforma2026
```

### Headers de Autenticação

```bash
# Para requisições para Mindchat
Authorization: Bearer your_mindchat_api_token
Content-Type: application/json

# Para webhooks do Mindchat
X-Mindchat-Signature: sha256=signature
X-Mindchat-Timestamp: timestamp
```

## Endpoints da API

### 1. Webhook de Recebimento de Mensagens

**Endpoint**: `POST /webhook/mindchat/whatsapp`

**Headers**:
```
Content-Type: application/json
X-Mindchat-Signature: sha256=...
X-Mindchat-Timestamp: ...
```

**Payload de Exemplo**:
```json
{
  "messages": [
    {
      "id": "wamid.xxx",
      "from": "5516999999999",
      "timestamp": "1640995200",
      "type": "text",
      "text": {
        "body": "Olá, preciso de ajuda com meu pedido"
      }
    }
  ],
  "contacts": [
    {
      "profile": {
        "name": "João Silva"
      },
      "wa_id": "5516999999999"
    }
  ]
}
```

**Resposta**:
```json
{
  "status": "success",
  "processed_messages": 1,
  "responses": [
    {
      "status": "processed",
      "message_id": "wamid.xxx",
      "response_text": "Olá João! Como posso ajudá-lo hoje?",
      "routing_action": "faq",
      "confidence": 0.85,
      "processed_at": "2024-01-14T10:30:00Z"
    }
  ]
}
```

### 2. Webhook de Status de Mensagens

**Endpoint**: `POST /webhook/mindchat/status`

**Payload de Exemplo**:
```json
{
  "statuses": [
    {
      "id": "wamid.xxx",
      "status": "delivered",
      "timestamp": "1640995200",
      "recipient_id": "5516999999999"
    }
  ]
}
```

### 3. Verificação de Webhook

**Endpoint**: `GET /webhook/mindchat/verify`

**Parâmetros**:
- `hub.mode`: "subscribe"
- `hub.challenge`: "challenge_string"
- `hub.verify_token`: "aria_verify_token"

### 4. Envio Manual de Mensagens

**Endpoint**: `POST /mindchat/send`

**Payload**:
```json
{
  "to": "5516999999999",
  "message": "Mensagem de teste",
  "message_type": "text"
}
```

## Tipos de Mensagem Suportados

### 1. Mensagens de Texto
```json
{
  "type": "text",
  "text": {
    "body": "Mensagem do usuário"
  }
}
```

### 2. Mensagens Interativas (Botões)
```json
{
  "type": "interactive",
  "interactive": {
    "type": "button_reply",
    "button_reply": {
      "id": "btn_faq",
      "title": "FAQ"
    }
  }
}
```

### 3. Mensagens Interativas (Lista)
```json
{
  "type": "interactive",
  "interactive": {
    "type": "list_reply",
    "list_reply": {
      "id": "list_option_1",
      "title": "Opção 1"
    }
  }
}
```

## Fluxos de Roteamento

### 1. FAQ (Perguntas Frequentes)
- **Trigger**: Palavras-chave como "horário", "preço", "como funciona"
- **Ação**: Usa RAG para buscar resposta na base de conhecimento
- **Resposta**: Resposta contextual baseada em FAQ

### 2. Agendamento
- **Trigger**: Palavras-chave como "agendar", "marcar", "consulta"
- **Ação**: Conecta com equipe de agendamentos
- **Resposta**: "📅 Entendi que você gostaria de agendar algo. Vou te conectar com nossa equipe de agendamentos."

### 3. Compra de Créditos
- **Trigger**: Palavras-chave como "comprar", "créditos", "pagamento"
- **Ação**: Conecta com equipe comercial
- **Resposta**: "💳 Perfeito! Vou te ajudar com a compra de créditos. Deixe-me conectar você com nossa equipe comercial."

### 4. Chat Padrão
- **Trigger**: Qualquer mensagem que não se encaixe nos fluxos acima
- **Ação**: Usa RAG para gerar resposta inteligente
- **Resposta**: Resposta contextual baseada no conhecimento geral

## Processamento RAG

### Integração com Supabase
```python
async def process_message_with_rag(message: WhatsAppMessage) -> str:
    """Processa mensagem usando RAG para gerar resposta inteligente"""
    
    rag_payload = {
        "query": message.text,
        "source": "faq",
        "user_id": message.from_number,
        "context": {
            "contact_name": message.contact_name,
            "message_type": message.message_type,
            "timestamp": message.timestamp
        }
    }
    
    response = requests.post(
        f"{ARIA_API_BASE_URL}/rag/query",
        json=rag_payload,
        headers={"Authorization": f"Bearer {FASTAPI_BEARER_TOKEN}"}
    )
    
    return response.json().get("answer", "Resposta padrão")
```

### Contexto Enriquecido
- **Nome do contato**: Personalização das respostas
- **Tipo de mensagem**: Diferentes tratamentos para texto/interativo
- **Timestamp**: Contexto temporal
- **Histórico**: Manutenção de contexto da conversa

## Segurança

### Validação de Assinatura
```python
def verify_mindchat_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verifica a assinatura do webhook do Mindchat"""
    
    expected_signature = hmac.new(
        MINDCHAT_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)
```

### Headers de Segurança
- **X-Mindchat-Signature**: Assinatura HMAC-SHA256
- **X-Mindchat-Timestamp**: Timestamp para prevenção de replay attacks
- **Authorization**: Bearer token para endpoints internos

## Monitoramento e Logs

### Logs Estruturados
```python
log.info(f"Webhook Mindchat recebido: {len(payload.get('messages', []))} mensagens")
log.info(f"Mensagem {message_id}: {status_type} em {timestamp}")
log.error(f"Erro ao processar webhook: {e}")
```

### Métricas Importantes
- **Mensagens recebidas**: Contador por tipo
- **Tempo de processamento**: Latência de resposta
- **Taxa de sucesso**: Percentual de mensagens processadas
- **Roteamento**: Distribuição por tipo de fluxo
- **Status de entrega**: Delivered, read, failed

## Testes

### Script de Teste Automatizado
```bash
python test_mindchat_integration.py
```

### Testes Incluídos
1. **Verificação de Webhook**: Validação do challenge
2. **Mensagem de Texto**: Processamento básico
3. **Mensagem Interativa**: Botões e listas
4. **Webhook de Status**: Status de entrega
5. **Envio Manual**: Teste de envio
6. **Validação de Assinatura**: Segurança
7. **Integração de Roteamento**: Fluxos inteligentes

### Exemplo de Teste Manual
```bash
curl -X POST http://localhost:8000/webhook/mindchat/whatsapp \
  -H "Content-Type: application/json" \
  -H "X-Mindchat-Signature: sha256=..." \
  -d '{
    "messages": [{
      "id": "wamid.test123",
      "from": "5516999999999",
      "timestamp": "1640995200",
      "type": "text",
      "text": {"body": "Qual é o horário de funcionamento?"}
    }],
    "contacts": [{
      "profile": {"name": "Cliente Teste"},
      "wa_id": "5516999999999"
    }]
  }'
```

## Configuração no Mindchat

### 1. Webhook URL
```
https://api.ar-online.com.br/webhook/mindchat/whatsapp
```

### 2. Verify Token
```
aria_verify_token
```

### 3. Eventos Configurados
- ✅ **messages**: Mensagens recebidas
- ✅ **message_deliveries**: Status de entrega
- ✅ **message_reads**: Status de leitura

### 4. Headers Personalizados
```
X-ARIA-Source: mindchat
X-ARIA-Version: 1.0
```

## Troubleshooting

### Problemas Comuns

1. **Webhook não recebe mensagens**
   - Verificar URL do webhook
   - Confirmar verify token
   - Verificar logs de erro

2. **Assinatura inválida**
   - Confirmar MINDCHAT_WEBHOOK_SECRET
   - Verificar algoritmo HMAC-SHA256
   - Validar timestamp

3. **RAG não responde**
   - Verificar conexão com Supabase
   - Confirmar API_TOKEN
   - Verificar logs de RAG

4. **Mensagens não são enviadas**
   - Confirmar MINDCHAT_API_TOKEN
   - Verificar formato da mensagem
   - Validar número de telefone

### Logs de Debug
```python
# Ativar logs detalhados
logging.basicConfig(level=logging.DEBUG)

# Logs específicos
log.debug(f"Payload recebido: {payload}")
log.debug(f"Assinatura esperada: {expected_signature}")
log.debug(f"Assinatura recebida: {signature}")
```

## Performance e Escalabilidade

### Otimizações Implementadas
- **Processamento assíncrono**: Não bloqueia o webhook
- **Timeout configurável**: Evita travamentos
- **Retry automático**: Para falhas temporárias
- **Cache de respostas**: Para perguntas frequentes

### Limites Recomendados
- **Timeout de webhook**: 10 segundos
- **Timeout de RAG**: 5 segundos
- **Timeout de envio**: 10 segundos
- **Rate limiting**: 100 mensagens/minuto

## Próximos Passos

1. **Configurar webhook no Mindchat**
2. **Testar com mensagens reais**
3. **Monitorar métricas de performance**
4. **Implementar templates de mensagem**
5. **Adicionar suporte a mídia**
6. **Integrar com CRM**

---

**ARIA-SDR** - Integração completa com Mindchat para WhatsApp inteligente 🤖📱
