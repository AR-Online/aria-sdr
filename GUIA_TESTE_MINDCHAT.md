# 🧪 Guia de Testes - Integração Mindchat ARIA-SDR

## 📋 Pré-requisitos

1. **Servidor rodando**: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
2. **Token Mindchat**: Configurado no `config.env.example`
3. **Ferramentas**: PowerShell ou terminal

## 🚀 Testes Básicos

### 1. Health Check
```powershell
# PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/mindchat/health" -Method GET

# Ou com curl
curl http://localhost:8000/mindchat/health
```

**Resultado esperado:**
```json
{
  "status": "healthy",
  "service": "ARIA Mindchat Integration Real",
  "version": "2.0.0",
  "api_base_url": "",
  "timestamp": "2025-10-14T20:00:41.498879"
}
```

### 2. Verificação de Webhook
```powershell
# PowerShell
$params = @{
    hub_mode = "subscribe"
    hub_challenge = "meu_teste_123"
    hub_verify_token = "aria_verify_token"
}
Invoke-RestMethod -Uri "http://localhost:8000/mindchat/webhook/verify" -Method GET -Body $params

# Ou com curl
curl "http://localhost:8000/mindchat/webhook/verify?hub_mode=subscribe&hub_challenge=meu_teste_123&hub_verify_token=aria_verify_token"
```

**Resultado esperado:** `"meu_teste_123"`

### 3. Envio de Mensagem
```powershell
# PowerShell
$params = @{
    to = "5516999999999"
    message = "Teste da ARIA-SDR via Mindchat"
    message_type = "text"
}
Invoke-RestMethod -Uri "http://localhost:8000/mindchat/send" -Method POST -Body $params

# Ou com curl
curl -X POST "http://localhost:8000/mindchat/send?to=5516999999999&message=Teste%20da%20ARIA-SDR&message_type=text"
```

## 🔧 Testes Avançados

### 4. Buscar Mensagens
```powershell
# PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/mindchat/messages?page=1&page_size=5" -Method GET

# Ou com curl
curl "http://localhost:8000/mindchat/messages?page=1&page_size=5"
```

### 5. Buscar Conversas
```powershell
# PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/mindchat/conversations" -Method GET

# Ou com curl
curl http://localhost:8000/mindchat/conversations
```

### 6. Criar Webhook
```powershell
# PowerShell
$params = @{
    webhook_url = "https://api.ar-online.com.br/webhook/mindchat/whatsapp"
    events = '["message", "status", "delivery"]'
}
Invoke-RestMethod -Uri "http://localhost:8000/mindchat/webhook/create" -Method POST -Body $params
```

## 📱 Teste de Webhook WhatsApp

### 7. Simular Recebimento de Mensagem
```powershell
# PowerShell
$headers = @{"Content-Type" = "application/json"}
$body = @{
    messages = @(
        @{
            id = "msg_123"
            from = "5516999999999"
            timestamp = "1640995200"
            type = "text"
            text = @{
                body = "Olá ARIA, como você está?"
            }
        }
    )
    contacts = @(
        @{
            profile = @{
                name = "João Silva"
            }
        }
    )
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri "http://localhost:8000/webhook/mindchat/whatsapp" -Method POST -Headers $headers -Body $body
```

## 🎯 Teste Automatizado Completo

### 8. Executar Script de Teste
```powershell
# Execute o script completo
python test_mindchat_real.py
```

**Resultado esperado:**
```
Testando integração Mindchat REAL da ARIA-SDR
============================================================
Testando health check Mindchat...
OK: Health check OK: healthy

Testando busca de mensagens Mindchat...
OK: Mensagens obtidas: error

Testando envio de mensagem Mindchat...
OK: Envio de mensagem OK: error

Testando criação de webhook Mindchat...
OK: Criação de webhook OK: error

Testando busca de conversas Mindchat...
OK: Conversas obtidas: error

Testando verificação de webhook Mindchat...
OK: Verificação de webhook OK

Testando recebimento de webhook Mindchat...
OK: Webhook recebido OK: success

============================================================
RESUMO DOS TESTES MINDCHAT REAL:
   Health Check: PASSOU
   Busca de Mensagens: PASSOU
   Envio de Mensagem: PASSOU
   Criação de Webhook: PASSOU
   Busca de Conversas: PASSOU
   Verificação de Webhook: PASSOU
   Recebimento de Webhook: PASSOU

Resultado: 7/7 testes passaram
Todos os testes passaram! Integração Mindchat REAL está funcionando!
```

## 🔍 Verificação de Logs

### 9. Monitorar Logs do Servidor
```powershell
# No terminal onde o servidor está rodando, você verá:
INFO: 127.0.0.1:xxxxx - "GET /mindchat/health HTTP/1.1" 200 OK
INFO: 127.0.0.1:xxxxx - "POST /mindchat/send HTTP/1.1" 200 OK
INFO: Webhook Mindchat real verificado com sucesso
```

## 🚨 Solução de Problemas

### Erro: "Invalid URL '/api/messages'"
**Causa:** URL base não configurada
**Solução:** Verificar `MINDCHAT_API_BASE_URL` no `.env`

### Erro: "422 Unprocessable Content"
**Causa:** Parâmetros incorretos
**Solução:** Verificar se está usando `to` em vez de `phone`

### Erro: "Webhook secret não configurado"
**Causa:** `MINDCHAT_WEBHOOK_SECRET` vazio
**Solução:** Configurar secret no `.env`

## 📊 Interpretação dos Resultados

- **Status "error"**: Normal para APIs externas em teste
- **Status "success"**: Indica que o endpoint funcionou
- **Status 200**: Requisição processada com sucesso
- **Status 422**: Parâmetros incorretos
- **Status 404**: Endpoint não encontrado

## 🎉 Próximos Passos

1. **Configurar webhook real** no painel Mindchat
2. **Testar com número real** do WhatsApp
3. **Integrar com RAG** da ARIA
4. **Monitorar em produção**

---

**💡 Dica:** Use o PowerShell ISE ou VS Code para executar os comandos mais facilmente!
