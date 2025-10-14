#!/usr/bin/env python3
"""
ARIA-SDR - GitLab Webhook Integration
Endpoint para receber e processar webhooks do GitLab
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import requests
from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aria_gitlab_webhook")

# Configurações
GITLAB_WEBHOOK_TOKEN = os.getenv("GITLAB_WEBHOOK_TOKEN", "dtransforma2026")
MINDCHAT_API_TOKEN = os.getenv("MINDCHAT_API_TOKEN")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "+5516997918658")
MINDCHAT_API_BASE_URL = os.getenv("MINDCHAT_API_BASE_URL", "https://api-aronline.mindchatapp.com.br")

# Modelos Pydantic
class GitLabWebhookPayload(BaseModel):
    event_type: str
    project_name: str
    aria_action: str
    timestamp: Optional[str] = None
    # Campos dinâmicos baseados no tipo de evento
    project_id: Optional[str] = None
    pipeline_status: Optional[str] = None
    pipeline_id: Optional[str] = None
    commit_sha: Optional[str] = None
    commit_message: Optional[str] = None
    branch: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    webhook_url: Optional[str] = None
    environment: Optional[str] = None
    deployment_status: Optional[str] = None
    deployment_id: Optional[str] = None
    merge_request_id: Optional[str] = None
    merge_request_title: Optional[str] = None
    merge_request_state: Optional[str] = None
    source_branch: Optional[str] = None
    target_branch: Optional[str] = None
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    commit_count: Optional[str] = None

class WebhookResponse(BaseModel):
    status: str
    message: str
    processed_at: str
    event_type: str

# Função para validar token
def validate_webhook_token(authorization: str = Header(None)) -> bool:
    """Valida o token de autorização do webhook"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    expected_token = f"Bearer {GITLAB_WEBHOOK_TOKEN}"
    if authorization != expected_token:
        raise HTTPException(status_code=401, detail="Invalid authorization token")
    
    return True

# Função para enviar notificação WhatsApp
async def send_whatsapp_notification(message: str, event_type: str = "gitlab_webhook") -> Dict[str, Any]:
    """Envia notificação via WhatsApp usando Mindchat API"""
    try:
        whatsapp_data = {
            "to": WHATSAPP_NUMBER,
            "message": f"🤖 ARIA Notification ({event_type}):\n{message}",
            "source": "gitlab_webhook",
            "timestamp": datetime.now().isoformat()
        }
        
        headers = {
            "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{MINDCHAT_API_BASE_URL}/webhook/whatsapp",
            json=whatsapp_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"Notificação WhatsApp enviada: {message}")
            return {"status": "success", "response": response.json()}
        else:
            logger.error(f"Erro ao enviar WhatsApp: {response.status_code} - {response.text}")
            return {"status": "error", "error": response.text}
            
    except Exception as e:
        logger.error(f"Erro ao enviar notificação WhatsApp: {e}")
        return {"status": "error", "error": str(e)}

# Funções de processamento de eventos
async def handle_pipeline_event(payload: GitLabWebhookPayload) -> WebhookResponse:
    """Processa eventos de pipeline"""
    project_name = payload.project_name
    pipeline_status = payload.pipeline_status
    commit_message = payload.commit_message or "Sem mensagem"
    branch = payload.branch or "branch desconhecida"
    
    if pipeline_status == "success":
        message = f"✅ Pipeline do {project_name} executado com sucesso!\n📝 Commit: {commit_message}\n🌿 Branch: {branch}"
        emoji = "✅"
    elif pipeline_status == "failed":
        message = f"❌ Pipeline do {project_name} falhou!\n📝 Commit: {commit_message}\n🌿 Branch: {branch}"
        emoji = "❌"
    elif pipeline_status == "running":
        message = f"🔄 Pipeline do {project_name} em andamento...\n📝 Commit: {commit_message}\n🌿 Branch: {branch}"
        emoji = "🔄"
    else:
        message = f"ℹ️ Pipeline do {project_name} - Status: {pipeline_status}\n📝 Commit: {commit_message}\n🌿 Branch: {branch}"
        emoji = "ℹ️"
    
    # Enviar notificação via WhatsApp
    whatsapp_result = await send_whatsapp_notification(message, "pipeline")
    
    return WebhookResponse(
        status="processed",
        message=f"{emoji} Pipeline {pipeline_status}",
        processed_at=datetime.now().isoformat(),
        event_type="pipeline"
    )

async def handle_deployment_event(payload: GitLabWebhookPayload) -> WebhookResponse:
    """Processa eventos de deploy"""
    project_name = payload.project_name
    environment = payload.environment or "ambiente desconhecido"
    deployment_status = payload.deployment_status
    commit_message = payload.commit_message or "Sem mensagem"
    
    if deployment_status == "success":
        message = f"🚀 Deploy do {project_name} para {environment} concluído!\n📝 Commit: {commit_message}"
        emoji = "🚀"
    elif deployment_status == "failed":
        message = f"💥 Deploy do {project_name} para {environment} falhou!\n📝 Commit: {commit_message}"
        emoji = "💥"
    elif deployment_status == "running":
        message = f"⏳ Deploy do {project_name} para {environment} em andamento...\n📝 Commit: {commit_message}"
        emoji = "⏳"
    else:
        message = f"ℹ️ Deploy do {project_name} para {environment} - Status: {deployment_status}\n📝 Commit: {commit_message}"
        emoji = "ℹ️"
    
    whatsapp_result = await send_whatsapp_notification(message, "deployment")
    
    return WebhookResponse(
        status="processed",
        message=f"{emoji} Deploy {deployment_status}",
        processed_at=datetime.now().isoformat(),
        event_type="deployment"
    )

async def handle_merge_request_event(payload: GitLabWebhookPayload) -> WebhookResponse:
    """Processa eventos de merge request"""
    project_name = payload.project_name
    mr_title = payload.merge_request_title or "Sem título"
    mr_state = payload.merge_request_state
    author_name = payload.author_name or "Autor desconhecido"
    
    if mr_state == "opened":
        message = f"📝 Nova MR no {project_name}:\n📋 Título: {mr_title}\n👤 Autor: {author_name}"
        emoji = "📝"
    elif mr_state == "merged":
        message = f"✅ MR mergeada no {project_name}:\n📋 Título: {mr_title}\n👤 Autor: {author_name}"
        emoji = "✅"
    elif mr_state == "closed":
        message = f"❌ MR fechada no {project_name}:\n📋 Título: {mr_title}\n👤 Autor: {author_name}"
        emoji = "❌"
    else:
        message = f"🔄 MR atualizada no {project_name}:\n📋 Título: {mr_title}\n👤 Autor: {author_name}\n📊 Status: {mr_state}"
        emoji = "🔄"
    
    whatsapp_result = await send_whatsapp_notification(message, "merge_request")
    
    return WebhookResponse(
        status="processed",
        message=f"{emoji} MR {mr_state}",
        processed_at=datetime.now().isoformat(),
        event_type="merge_request"
    )

async def handle_push_event(payload: GitLabWebhookPayload) -> WebhookResponse:
    """Processa eventos de push"""
    project_name = payload.project_name
    commit_message = payload.commit_message or "Sem mensagem"
    branch = payload.branch or "branch desconhecida"
    commit_count = payload.commit_count or "1"
    user_name = payload.user_name or "Usuário desconhecido"
    
    message = f"📤 Push no {project_name}:\n🌿 Branch: {branch}\n📝 Commit: {commit_message}\n📊 Commits: {commit_count}\n👤 Autor: {user_name}"
    
    whatsapp_result = await send_whatsapp_notification(message, "push")
    
    return WebhookResponse(
        status="processed",
        message="📤 Push processado",
        processed_at=datetime.now().isoformat(),
        event_type="push"
    )

# Endpoint principal do webhook
async def gitlab_webhook_endpoint(
    request: Request,
    payload: Dict[str, Any],
    _: bool = Depends(validate_webhook_token)
) -> WebhookResponse:
    """Endpoint principal para receber webhooks do GitLab"""
    
    logger.info(f"Webhook GitLab recebido: {payload.get('aria_action', 'unknown')}")
    
    try:
        # Converter payload para modelo Pydantic
        webhook_payload = GitLabWebhookPayload(**payload)
        
        # Processar evento baseado no tipo
        event_type = webhook_payload.aria_action
        
        if event_type == "pipeline_notification":
            result = await handle_pipeline_event(webhook_payload)
        elif event_type == "deployment_notification":
            result = await handle_deployment_event(webhook_payload)
        elif event_type == "merge_request_notification":
            result = await handle_merge_request_event(webhook_payload)
        elif event_type == "push_notification":
            result = await handle_push_event(webhook_payload)
        else:
            logger.warning(f"Tipo de evento não reconhecido: {event_type}")
            result = WebhookResponse(
                status="ignored",
                message=f"Evento {event_type} ignorado",
                processed_at=datetime.now().isoformat(),
                event_type=event_type
            )
        
        logger.info(f"Webhook processado com sucesso: {result.status}")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# Endpoint de health check
async def webhook_health_check() -> Dict[str, str]:
    """Health check para o webhook"""
    return {
        "status": "healthy",
        "service": "ARIA GitLab Webhook",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Endpoint de teste
async def test_webhook(
    test_payload: Dict[str, Any],
    _: bool = Depends(validate_webhook_token)
) -> WebhookResponse:
    """Endpoint para testar webhook"""
    
    logger.info("Teste de webhook iniciado")
    
    # Adicionar dados de teste se não fornecidos
    if "aria_action" not in test_payload:
        test_payload["aria_action"] = "pipeline_notification"
    if "project_name" not in test_payload:
        test_payload["project_name"] = "aria-sdr-test"
    if "pipeline_status" not in test_payload:
        test_payload["pipeline_status"] = "success"
    
    # Processar como webhook normal
    return await gitlab_webhook_endpoint(None, test_payload, True)

if __name__ == "__main__":
    print("ARIA-SDR GitLab Webhook Integration")
    print("Configurações:")
    print(f"- Token: {GITLAB_WEBHOOK_TOKEN[:10]}...")
    print(f"- WhatsApp: {WHATSAPP_NUMBER}")
    print(f"- Mindchat API: {MINDCHAT_API_BASE_URL}")
    print("\nPara usar, importe as funções em sua aplicação FastAPI:")
    print("from aria_gitlab_webhook import gitlab_webhook_endpoint, webhook_health_check")
