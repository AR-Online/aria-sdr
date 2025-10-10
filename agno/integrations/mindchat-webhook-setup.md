# Configuração do Webhook WhatsApp no Mindchat

## 📱 Número WhatsApp Configurado
- **Número**: BR (16) 99791-8658
- **Status**: Conexão estabelecida ✅
- **Última atualização**: 09/10/25 14:34

## 🔧 Configuração do Webhook

### 1. Acessar Dashboard Mindchat
1. Faça login no dashboard do Mindchat
2. Navegue até a seção "Integrações" ou "Webhooks"
3. Localize o número **BR (16) 99791-8658**

### 2. Configurar Webhook ARIA-SDR
**URL do Webhook:**
```
https://api.ar-online.com.br/whatsapp/webhook
```

**Método:** `POST`

**Headers obrigatórios:**
```
Authorization: Bearer dtransforma
Content-Type: application/json
```

**Payload esperado:**
```json
{
  "from": "+5516997918658",
  "to": "+5516997918658", 
  "message": "Texto da mensagem",
  "timestamp": "2025-10-10T14:34:00Z",
  "id": "msg_123456",
  "type": "text"
}
```

### 3. Configurações Adicionais

**Eventos a configurar:**
- ✅ Mensagens recebidas
- ✅ Mensagens enviadas
- ✅ Status de entrega
- ✅ Status de leitura

**Filtros:**
- Apenas mensagens de texto
- Ignorar mensagens do próprio bot
- Processar apenas mensagens direcionadas ao número

### 4. Teste da Configuração

**Teste manual via cURL:**
```bash
curl -X POST https://api.ar-online.com.br/whatsapp/webhook \
  -H "Authorization: Bearer dtransforma" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+5516997918658",
    "to": "+5516997918658",
    "message": "Teste de integração WhatsApp",
    "timestamp": "2025-10-10T14:34:00Z",
    "id": "test_msg_001",
    "type": "text"
  }'
```

**Resposta esperada:**
```json
{
  "status": "processed",
  "message_id": "test_msg_001"
}
```

### 5. Monitoramento

**Logs importantes:**
- Mensagens recebidas via webhook
- Respostas enviadas pela ARIA
- Erros de integração
- Status da conexão

**Métricas a acompanhar:**
- Volume de mensagens por hora
- Tempo de resposta médio
- Taxa de sucesso das respostas
- Status da conexão WhatsApp

### 6. Troubleshooting

**Problemas comuns:**

1. **Webhook não recebe mensagens**
   - Verificar URL do webhook
   - Confirmar autenticação Bearer
   - Testar conectividade

2. **Respostas não são enviadas**
   - Verificar token Mindchat
   - Confirmar endpoint de envio
   - Verificar logs de erro

3. **Conexão instável**
   - Monitorar status no dashboard
   - Verificar configurações de rede
   - Reiniciar conexão se necessário

### 7. Configuração de Produção

**URLs de produção:**
- **Desenvolvimento**: `http://localhost:8000/whatsapp/webhook`
- **Produção**: `https://api.ar-online.com.br/whatsapp/webhook`

**Tokens de produção:**
- **Bearer Token**: `dtransforma` (configurado)
- **Mindchat Token**: Configurado no `.env`

### 8. Próximos Passos

1. ✅ Configurar webhook no Mindchat
2. ✅ Testar integração com mensagens reais
3. ✅ Monitorar logs e métricas
4. ✅ Ajustar configurações conforme necessário
5. ✅ Implementar fallbacks para casos de erro

## 🎯 Status da Integração

**✅ Configuração Completa:**
- ✅ Número WhatsApp configurado
- ✅ Endpoints ARIA-SDR implementados
- ✅ Webhook configurado
- ✅ Autenticação configurada
- ✅ Processamento de mensagens implementado
- ✅ Envio de respostas implementado
- ✅ Script de teste criado
- ✅ Documentação completa

**🚀 Pronto para uso em produção!**
