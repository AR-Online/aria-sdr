# Mindchat Integration for ARIA-SDR

## Visão Geral

A integração com Mindchat permite que a ARIA-SDR:
- Receba mensagens do WhatsApp via webhook
- Processe mensagens usando RAG (Retrieval Augmented Generation)
- Envie respostas inteligentes via API do Mindchat
- Gerencie diferentes tipos de fluxos (FAQ, agendamento, vendas)

## Configuração

### Variáveis de Ambiente
```bash
# Mindchat API Configuration
MINDCHAT_API_TOKEN=your_mindchat_api_token
MINDCHAT_API_BASE_URL=https://api-aronline.mindchat.com
MINDCHAT_API_DOCS=https://docs.mindchat.com

# WhatsApp Configuration
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_WEBHOOK_URL=https://api.ar-online.com.br/webhook/mindchat/whatsapp
WHATSAPP_VERIFY_TOKEN=your_verify_token

# ARIA Configuration
ARIA_WEBHOOK_URL=https://api.ar-online.com.br/webhook/assist/routing
ARIA_API_BASE_URL=https://api.ar-online.com.br
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

### 1. Webhook de Recebimento (Mindchat → ARIA)
```http
POST /webhook/mindchat/whatsapp
Content-Type: application/json
X-Mindchat-Signature: sha256=...

{
  "message": {
    "id": "wamid.xxx",
    "from": "5516999999999",
    "timestamp": "1640995200",
    "text": {
      "body": "Olá, preciso de ajuda com meu pedido"
    },
    "type": "text"
  },
  "contact": {
    "profile": {
      "name": "João Silva"
    },
    "wa_id": "5516999999999"
  },
  "context": {
    "from": "5516999999999",
    "id": "wamid.xxx"
  }
}
```

### 2. Envio de Mensagem (ARIA → Mindchat)
```http
POST https://api-aronline.mindchat.com/messages
Authorization: Bearer your_mindchat_api_token
Content-Type: application/json

{
  "messaging_product": "whatsapp",
  "to": "5516999999999",
  "type": "text",
  "text": {
    "body": "Olá João! Como posso ajudá-lo hoje?"
  }
}
```

### 3. Webhook de Status (Mindchat → ARIA)
```http
POST /webhook/mindchat/status
Content-Type: application/json

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

## Implementação Python

### Classe Principal de Integração
```python
import os
import json
import hmac
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import requests
from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configurações
MINDCHAT_API_TOKEN = os.getenv("MINDCHAT_API_TOKEN")
MINDCHAT_API_BASE_URL = os.getenv("MINDCHAT_API_BASE_URL", "https://api-aronline.mindchat.com")
MINDCHAT_WEBHOOK_SECRET = os.getenv("MINDCHAT_WEBHOOK_SECRET", "your_webhook_secret")
ARIA_API_BASE_URL = os.getenv("ARIA_API_BASE_URL", "https://api.ar-online.com.br")

logger = logging.getLogger(__name__)

@dataclass
class WhatsAppMessage:
    """Representa uma mensagem do WhatsApp"""
    message_id: str
    from_number: str
    timestamp: str
    text: str
    message_type: str
    contact_name: Optional[str] = None
    context_id: Optional[str] = None

@dataclass
class WhatsAppContact:
    """Representa um contato do WhatsApp"""
    wa_id: str
    name: Optional[str] = None
    profile_name: Optional[str] = None

class MindchatIntegration:
    """Classe principal para integração com Mindchat"""
    
    def __init__(self):
        self.api_token = MINDCHAT_API_TOKEN
        self.base_url = MINDCHAT_API_BASE_URL
        self.webhook_secret = MINDCHAT_WEBHOOK_SECRET
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        })
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verifica a assinatura do webhook do Mindchat"""
        if not self.webhook_secret:
            logger.warning("Webhook secret não configurado, pulando verificação")
            return True
        
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    def parse_whatsapp_message(self, payload: Dict[str, Any]) -> Optional[WhatsAppMessage]:
        """Converte payload do Mindchat para objeto WhatsAppMessage"""
        try:
            if "messages" not in payload:
                return None
            
            message_data = payload["messages"][0]
            contact_data = payload.get("contacts", [{}])[0]
            
            # Extrair texto da mensagem
            text = ""
            message_type = message_data.get("type", "text")
            
            if message_type == "text":
                text = message_data.get("text", {}).get("body", "")
            elif message_type == "interactive":
                interactive = message_data.get("interactive", {})
                if interactive.get("type") == "button_reply":
                    text = interactive.get("button_reply", {}).get("title", "")
                elif interactive.get("type") == "list_reply":
                    text = interactive.get("list_reply", {}).get("title", "")
            
            return WhatsAppMessage(
                message_id=message_data.get("id", ""),
                from_number=message_data.get("from", ""),
                timestamp=message_data.get("timestamp", ""),
                text=text,
                message_type=message_type,
                contact_name=contact_data.get("profile", {}).get("name"),
                context_id=message_data.get("context", {}).get("id")
            )
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem WhatsApp: {e}")
            return None
    
    async def send_message(self, to: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """Envia mensagem via API do Mindchat"""
        try:
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": message_type,
                "text": {"body": message}
            }
            
            response = self.session.post(
                f"{self.base_url}/messages",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Mensagem enviada para {to}: {message[:50]}...")
                return {"status": "success", "response": result}
            else:
                logger.error(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
                return {"status": "error", "error": response.text}
                
        except Exception as e:
            logger.error(f"Exceção ao enviar mensagem: {e}")
            return {"status": "error", "error": str(e)}
    
    async def send_template_message(self, to: str, template_name: str, 
                                  parameters: List[str]) -> Dict[str, Any]:
        """Envia mensagem usando template aprovado"""
        try:
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": "pt_BR"},
                    "components": [
                        {
                            "type": "body",
                            "parameters": [{"type": "text", "text": param} for param in parameters]
                        }
                    ]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/messages",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Template {template_name} enviado para {to}")
                return {"status": "success", "response": result}
            else:
                logger.error(f"Erro ao enviar template: {response.status_code} - {response.text}")
                return {"status": "error", "error": response.text}
                
        except Exception as e:
            logger.error(f"Exceção ao enviar template: {e}")
            return {"status": "error", "error": str(e)}
    
    async def process_message_with_rag(self, message: WhatsAppMessage) -> str:
        """Processa mensagem usando RAG para gerar resposta inteligente"""
        try:
            # Chamar API de RAG da ARIA
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
                headers={"Authorization": f"Bearer {os.getenv('FASTAPI_BEARER_TOKEN')}"},
                timeout=10
            )
            
            if response.status_code == 200:
                rag_result = response.json()
                return rag_result.get("answer", "Desculpe, não consegui processar sua mensagem.")
            else:
                logger.error(f"Erro na API RAG: {response.status_code}")
                return "Desculpe, estou com dificuldades técnicas. Tente novamente em alguns minutos."
                
        except Exception as e:
            logger.error(f"Erro ao processar RAG: {e}")
            return "Desculpe, ocorreu um erro interno. Tente novamente mais tarde."
    
    async def route_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Roteia mensagem para o fluxo apropriado"""
        try:
            # Chamar API de roteamento da ARIA
            routing_payload = {
                "message": message.text,
                "user_id": message.from_number,
                "contact_name": message.contact_name,
                "message_type": message.message_type,
                "timestamp": message.timestamp
            }
            
            response = requests.post(
                f"{ARIA_API_BASE_URL}/assist/routing",
                json=routing_payload,
                headers={"Authorization": f"Bearer {os.getenv('FASTAPI_BEARER_TOKEN')}"},
                timeout=10
            )
            
            if response.status_code == 200:
                routing_result = response.json()
                return {
                    "status": "success",
                    "routing": routing_result,
                    "action": routing_result.get("action", "chat"),
                    "confidence": routing_result.get("confidence", 0.0)
                }
            else:
                logger.error(f"Erro na API de roteamento: {response.status_code}")
                return {"status": "error", "action": "chat", "confidence": 0.0}
                
        except Exception as e:
            logger.error(f"Erro ao rotear mensagem: {e}")
            return {"status": "error", "action": "chat", "confidence": 0.0}

# Instância global
mindchat = MindchatIntegration()

# Modelos Pydantic para FastAPI
class WhatsAppWebhookPayload(BaseModel):
    """Payload do webhook do WhatsApp via Mindchat"""
    messages: List[Dict[str, Any]]
    contacts: List[Dict[str, Any]]
    statuses: Optional[List[Dict[str, Any]]] = None

class MessageResponse(BaseModel):
    """Resposta de processamento de mensagem"""
    status: str
    message_id: str
    response_text: str
    routing_action: str
    confidence: float
    processed_at: str

# Endpoints FastAPI
@app.post("/webhook/mindchat/whatsapp")
async def whatsapp_webhook(
    request: Request,
    payload: WhatsAppWebhookPayload,
    x_mindchat_signature: str = Header(None),
    x_mindchat_timestamp: str = Header(None)
) -> JSONResponse:
    """Endpoint principal para receber webhooks do Mindchat"""
    
    # Verificar assinatura
    body = await request.body()
    if not mindchat.verify_webhook_signature(body, x_mindchat_signature or ""):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    logger.info(f"Webhook Mindchat recebido: {len(payload.messages)} mensagens")
    
    try:
        # Processar cada mensagem
        responses = []
        
        for message_data in payload.messages:
            # Converter para objeto WhatsAppMessage
            whatsapp_msg = mindchat.parse_whatsapp_message({
                "messages": [message_data],
                "contacts": payload.contacts
            })
            
            if not whatsapp_msg:
                continue
            
            # Roteamento inteligente
            routing_result = await mindchat.route_message(whatsapp_msg)
            
            # Processar baseado no roteamento
            if routing_result["action"] == "faq":
                # Usar RAG para responder FAQ
                response_text = await mindchat.process_message_with_rag(whatsapp_msg)
                
            elif routing_result["action"] == "schedule":
                # Fluxo de agendamento
                response_text = "📅 Entendi que você gostaria de agendar algo. Vou te conectar com nossa equipe de agendamentos."
                
            elif routing_result["action"] == "buy_credits":
                # Fluxo de compra de créditos
                response_text = "💳 Perfeito! Vou te ajudar com a compra de créditos. Deixe-me conectar você com nossa equipe comercial."
                
            else:
                # Chat padrão com RAG
                response_text = await mindchat.process_message_with_rag(whatsapp_msg)
            
            # Enviar resposta
            send_result = await mindchat.send_message(
                whatsapp_msg.from_number,
                response_text
            )
            
            responses.append(MessageResponse(
                status="processed",
                message_id=whatsapp_msg.message_id,
                response_text=response_text,
                routing_action=routing_result["action"],
                confidence=routing_result["confidence"],
                processed_at=datetime.now().isoformat()
            ))
        
        return JSONResponse(content={
            "status": "success",
            "processed_messages": len(responses),
            "responses": [r.dict() for r in responses]
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/webhook/mindchat/status")
async def status_webhook(
    payload: Dict[str, Any],
    x_mindchat_signature: str = Header(None)
) -> JSONResponse:
    """Endpoint para receber status de mensagens"""
    
    logger.info(f"Status webhook recebido: {payload}")
    
    # Processar status (delivered, read, failed)
    for status in payload.get("statuses", []):
        message_id = status.get("id")
        status_type = status.get("status")
        timestamp = status.get("timestamp")
        
        logger.info(f"Mensagem {message_id}: {status_type} em {timestamp}")
    
    return JSONResponse(content={"status": "received"})

@app.get("/webhook/mindchat/verify")
async def verify_webhook(
    hub_mode: str,
    hub_challenge: str,
    hub_verify_token: str
) -> str:
    """Verificação do webhook (requerido pelo Mindchat)"""
    
    verify_token = os.getenv("MINDCHAT_VERIFY_TOKEN", "your_verify_token")
    
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        logger.info("Webhook verificado com sucesso")
        return hub_challenge
    else:
        raise HTTPException(status_code=403, detail="Verification failed")

# Endpoint para envio manual de mensagens
@app.post("/mindchat/send")
async def send_manual_message(
    to: str,
    message: str,
    message_type: str = "text"
) -> JSONResponse:
    """Endpoint para envio manual de mensagens"""
    
    result = await mindchat.send_message(to, message, message_type)
    
    return JSONResponse(content=result)

# Endpoint para envio de templates
@app.post("/mindchat/send-template")
async def send_template_message(
    to: str,
    template_name: str,
    parameters: List[str]
) -> JSONResponse:
    """Endpoint para envio de mensagens template"""
    
    result = await mindchat.send_template_message(to, template_name, parameters)
    
    return JSONResponse(content=result)

if __name__ == "__main__":
    print("ARIA-SDR Mindchat Integration")
    print(f"API Base URL: {MINDCHAT_API_BASE_URL}")
    print(f"Webhook Secret: {'*' * 10 if MINDCHAT_WEBHOOK_SECRET else 'Not configured'}")
    print("\nEndpoints disponíveis:")
    print("- POST /webhook/mindchat/whatsapp")
    print("- POST /webhook/mindchat/status")
    print("- GET /webhook/mindchat/verify")
    print("- POST /mindchat/send")
    print("- POST /mindchat/send-template")
