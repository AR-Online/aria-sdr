#!/usr/bin/env python3
"""
ARIA-SDR - Integração Mindchat Atualizada
Baseada na API real descoberta: https://api-aronline.mindchatapp.com.br/api-docs/
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

import requests
from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aria_mindchat_real")

# Configurações reais do Mindchat
MINDCHAT_API_TOKEN = os.getenv("MINDCHAT_API_TOKEN", "c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58")
MINDCHAT_API_BASE_URL = os.getenv("MINDCHAT_API_BASE_URL", "https://api-aronline.mindchatapp.com.br")
MINDCHAT_WEBHOOK_SECRET = os.getenv("MINDCHAT_WEBHOOK_SECRET", "aria_webhook_secret")
MINDCHAT_VERIFY_TOKEN = os.getenv("MINDCHAT_VERIFY_TOKEN", "aria_verify_token")

class MindchatMessage(BaseModel):
    """Modelo para mensagem do Mindchat"""
    id: str
    phone: str
    message: str
    type: str = "text"
    contact_name: Optional[str] = None
    created_at: Optional[str] = None
    ack: Optional[int] = None
    read: Optional[bool] = None

class MindchatWebhookPayload(BaseModel):
    """Payload do webhook do Mindchat"""
    messages: Optional[List[Dict[str, Any]]] = None
    statuses: Optional[List[Dict[str, Any]]] = None
    contacts: Optional[List[Dict[str, Any]]] = None

class MindchatIntegration:
    """Classe principal para integração com Mindchat API real"""
    
    def __init__(self):
        self.api_token = MINDCHAT_API_TOKEN
        self.base_url = MINDCHAT_API_BASE_URL
        self.webhook_secret = MINDCHAT_WEBHOOK_SECRET
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        })
    
    async def get_messages(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Busca mensagens do Mindchat"""
        try:
            params = {
                "page": page,
                "pageSize": page_size
            }
            
            response = self.session.get(
                f"{self.base_url}/api/messages",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Mensagens obtidas: {data.get('count', 0)} total")
                return {"status": "success", "data": data}
            else:
                logger.error(f"Erro ao buscar mensagens: {response.status_code}")
                return {"status": "error", "error": response.text}
                
        except Exception as e:
            logger.error(f"Exceção ao buscar mensagens: {e}")
            return {"status": "error", "error": str(e)}
    
    async def send_message(self, phone: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """Envia mensagem via API real do Mindchat"""
        try:
            payload = {
                "phone": phone,
                "message": message,
                "type": message_type
            }
            
            response = self.session.post(
                f"{self.base_url}/api/send",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Mensagem enviada para {phone}: {message[:50]}...")
                return {"status": "success", "response": data}
            else:
                logger.error(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
                return {"status": "error", "error": response.text}
                
        except Exception as e:
            logger.error(f"Exceção ao enviar mensagem: {e}")
            return {"status": "error", "error": str(e)}
    
    async def create_webhook(self, webhook_url: str, events: List[str] = None) -> Dict[str, Any]:
        """Cria webhook no Mindchat"""
        try:
            if events is None:
                events = ["message", "status", "delivery"]
            
            payload = {
                "url": webhook_url,
                "events": events,
                "verify_token": MINDCHAT_VERIFY_TOKEN,
                "active": True,
                "description": "ARIA-SDR Webhook Integration"
            }
            
            response = self.session.post(
                f"{self.base_url}/webhook",
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                logger.info(f"Webhook criado: {webhook_url}")
                return {"status": "success", "response": data}
            else:
                logger.error(f"Erro ao criar webhook: {response.status_code} - {response.text}")
                return {"status": "error", "error": response.text}
                
        except Exception as e:
            logger.error(f"Exceção ao criar webhook: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_conversations(self) -> Dict[str, Any]:
        """Busca conversas do Mindchat"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/conversations",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Conversas obtidas com sucesso")
                return {"status": "success", "data": data}
            else:
                logger.error(f"Erro ao buscar conversas: {response.status_code}")
                return {"status": "error", "error": response.text}
                
        except Exception as e:
            logger.error(f"Exceção ao buscar conversas: {e}")
            return {"status": "error", "error": str(e)}
    
    def parse_mindchat_message(self, message_data: Dict[str, Any]) -> Optional[MindchatMessage]:
        """Converte dados do Mindchat para objeto MindchatMessage"""
        try:
            return MindchatMessage(
                id=message_data.get("id", ""),
                phone=message_data.get("phone", ""),
                message=message_data.get("text", ""),
                type=message_data.get("type", "text"),
                contact_name=message_data.get("contact", {}).get("name"),
                created_at=message_data.get("createdAt"),
                ack=message_data.get("ack"),
                read=message_data.get("read")
            )
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return None

# Instância global
mindchat = MindchatIntegration()

# Endpoints FastAPI
app = FastAPI(title="ARIA-SDR Mindchat Integration")

@app.get("/mindchat/health")
async def mindchat_health() -> JSONResponse:
    """Health check da integração Mindchat"""
    return JSONResponse(content={
        "status": "healthy",
        "service": "ARIA Mindchat Integration",
        "version": "2.0.0",
        "api_base_url": MINDCHAT_API_BASE_URL,
        "timestamp": datetime.now().isoformat()
    })

@app.get("/mindchat/messages")
async def get_mindchat_messages(
    page: int = 1,
    page_size: int = 20
) -> JSONResponse:
    """Endpoint para buscar mensagens do Mindchat"""
    
    result = await mindchat.get_messages(page, page_size)
    
    return JSONResponse(content=result)

@app.post("/mindchat/send")
async def send_mindchat_message(
    phone: str,
    message: str,
    message_type: str = "text"
) -> JSONResponse:
    """Endpoint para envio de mensagem via Mindchat"""
    
    result = await mindchat.send_message(phone, message, message_type)
    
    return JSONResponse(content=result)

@app.post("/mindchat/webhook/create")
async def create_mindchat_webhook(
    webhook_url: str,
    events: List[str] = None
) -> JSONResponse:
    """Endpoint para criar webhook no Mindchat"""
    
    result = await mindchat.create_webhook(webhook_url, events)
    
    return JSONResponse(content=result)

@app.get("/mindchat/conversations")
async def get_mindchat_conversations() -> JSONResponse:
    """Endpoint para buscar conversas do Mindchat"""
    
    result = await mindchat.get_conversations()
    
    return JSONResponse(content=result)

@app.post("/webhook/mindchat/whatsapp")
async def mindchat_whatsapp_webhook(
    request: Request,
    payload: MindchatWebhookPayload
) -> JSONResponse:
    """Endpoint para receber webhooks do Mindchat"""
    
    logger.info(f"Webhook Mindchat recebido: {payload}")
    
    try:
        responses = []
        
        # Processar mensagens se existirem
        if payload.messages:
            for message_data in payload.messages:
                message = mindchat.parse_mindchat_message(message_data)
                
                if message:
                    # Aqui você pode integrar com RAG, roteamento, etc.
                    logger.info(f"Mensagem processada: {message.id} de {message.phone}")
                    
                    responses.append({
                        "message_id": message.id,
                        "phone": message.phone,
                        "processed": True,
                        "processed_at": datetime.now().isoformat()
                    })
        
        # Processar status se existirem
        if payload.statuses:
            for status_data in payload.statuses:
                logger.info(f"Status recebido: {status_data}")
        
        return JSONResponse(content={
            "status": "success",
            "processed_messages": len(responses),
            "responses": responses,
            "processed_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/mindchat/webhook/verify")
async def verify_mindchat_webhook(
    hub_mode: str,
    hub_challenge: str,
    hub_verify_token: str
) -> str:
    """Verificação do webhook Mindchat"""
    
    if hub_mode == "subscribe" and hub_verify_token == MINDCHAT_VERIFY_TOKEN:
        logger.info("Webhook Mindchat verificado com sucesso")
        return hub_challenge
    else:
        raise HTTPException(status_code=403, detail="Verification failed")

if __name__ == "__main__":
    print("ARIA-SDR Mindchat Integration v2.0")
    print(f"API Base URL: {MINDCHAT_API_BASE_URL}")
    print(f"Token: {MINDCHAT_API_TOKEN[:20]}...")
    print("\nEndpoints disponíveis:")
    print("- GET /mindchat/health")
    print("- GET /mindchat/messages")
    print("- POST /mindchat/send")
    print("- POST /mindchat/webhook/create")
    print("- GET /mindchat/conversations")
    print("- POST /webhook/mindchat/whatsapp")
    print("- GET /mindchat/webhook/verify")
