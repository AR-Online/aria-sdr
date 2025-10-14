# GitLab Webhook Configuration for ARIA-SDR

## Webhook Template Personalizado

### Template para Eventos de Pipeline

```json
{
  "event_type": "pipeline",
  "project_name": "{{project.name}}",
  "project_id": "{{project.id}}",
  "pipeline_status": "{{builds[0].status}}",
  "pipeline_id": "{{builds[0].id}}",
  "commit_sha": "{{commits[0].id}}",
  "commit_message": "{{commits[0].message}}",
  "branch": "{{ref}}",
  "user_name": "{{user.name}}",
  "user_email": "{{user.email}}",
  "webhook_url": "{{project.web_url}}",
  "timestamp": "{{builds[0].created_at}}",
  "aria_action": "pipeline_notification"
}
```

### Template para Eventos de Deploy

```json
{
  "event_type": "deployment",
  "project_name": "{{project.name}}",
  "environment": "{{environment.name}}",
  "deployment_status": "{{deployable.status}}",
  "deployment_id": "{{deployable.id}}",
  "commit_sha": "{{commit.id}}",
  "commit_message": "{{commit.message}}",
  "branch": "{{ref}}",
  "user_name": "{{user.name}}",
  "deployment_url": "{{environment.external_url}}",
  "timestamp": "{{deployable.created_at}}",
  "aria_action": "deployment_notification"
}
```

### Template para Eventos de Merge Request

```json
{
  "event_type": "merge_request",
  "project_name": "{{project.name}}",
  "merge_request_id": "{{object_attributes.id}}",
  "merge_request_title": "{{object_attributes.title}}",
  "merge_request_state": "{{object_attributes.state}}",
  "source_branch": "{{object_attributes.source_branch}}",
  "target_branch": "{{object_attributes.target_branch}}",
  "author_name": "{{user.name}}",
  "author_email": "{{user.email}}",
  "webhook_url": "{{object_attributes.url}}",
  "timestamp": "{{object_attributes.created_at}}",
  "aria_action": "merge_request_notification"
}
```

### Template para Eventos de Push

```json
{
  "event_type": "push",
  "project_name": "{{project.name}}",
  "commit_count": "{{total_commits_count}}",
  "commit_sha": "{{commits[0].id}}",
  "commit_message": "{{commits[0].message}}",
  "branch": "{{ref}}",
  "user_name": "{{user.name}}",
  "user_email": "{{user.email}}",
  "webhook_url": "{{project.web_url}}",
  "timestamp": "{{commits[0].timestamp}}",
  "aria_action": "push_notification"
}
```

## Configuração no GitLab

### 1. URL do Webhook

```
https://api.ar-online.com.br/webhook/gitlab/aria
```

### 2. Token Secreto

```
ARIA_GITLAB_WEBHOOK_TOKEN=dtransforma2026
```

### 3. Eventos Selecionados

- ✅ **Eventos de implantação** (Deployment events)
- ✅ **Eventos de lançamentos** (Release events)
- ✅ **Eventos de marco** (Milestone events)
- ✅ **Eventos de vulnerabilidade** (Vulnerability events)
- ✅ **Push events** (para commits)
- ✅ **Merge request events** (para PRs)

### 4. Headers Personalizados

```
Content-Type: application/json
X-ARIA-Source: gitlab
X-ARIA-Version: 1.0
Authorization: Bearer dtransforma2026
```

## Endpoint ARIA para Receber Webhooks

### Estrutura do Endpoint

```python
@app.post("/webhook/gitlab/aria")
async def gitlab_webhook(
    request: Request,
    payload: dict,
    authorization: str = Header(None)
):
    """Endpoint para receber webhooks do GitLab"""
    
    # Validar token
    if authorization != "Bearer dtransforma2026":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Processar evento
    event_type = payload.get("aria_action")
    
    if event_type == "pipeline_notification":
        return await handle_pipeline_event(payload)
    elif event_type == "deployment_notification":
        return await handle_deployment_event(payload)
    elif event_type == "merge_request_notification":
        return await handle_merge_request_event(payload)
    elif event_type == "push_notification":
        return await handle_push_event(payload)
    else:
        return {"status": "ignored", "reason": "unknown_event"}
```

### Funções de Processamento

```python
async def handle_pipeline_event(payload: dict):
    """Processa eventos de pipeline"""
    project_name = payload.get("project_name")
    pipeline_status = payload.get("pipeline_status")
    
    if pipeline_status == "success":
        message = f"✅ Pipeline do {project_name} executado com sucesso!"
    elif pipeline_status == "failed":
        message = f"❌ Pipeline do {project_name} falhou!"
    else:
        message = f"🔄 Pipeline do {project_name} em andamento..."
    
    # Enviar notificação via WhatsApp
    await send_whatsapp_notification(message)
    
    return {"status": "processed", "message": message}

async def handle_deployment_event(payload: dict):
    """Processa eventos de deploy"""
    project_name = payload.get("project_name")
    environment = payload.get("environment")
    deployment_status = payload.get("deployment_status")
    
    if deployment_status == "success":
        message = f"🚀 Deploy do {project_name} para {environment} concluído!"
    elif deployment_status == "failed":
        message = f"💥 Deploy do {project_name} para {environment} falhou!"
    else:
        message = f"⏳ Deploy do {project_name} para {environment} em andamento..."
    
    await send_whatsapp_notification(message)
    
    return {"status": "processed", "message": message}

async def handle_merge_request_event(payload: dict):
    """Processa eventos de merge request"""
    project_name = payload.get("project_name")
    mr_title = payload.get("merge_request_title")
    mr_state = payload.get("merge_request_state")
    
    if mr_state == "opened":
        message = f"📝 Nova MR no {project_name}: {mr_title}"
    elif mr_state == "merged":
        message = f"✅ MR mergeada no {project_name}: {mr_title}"
    elif mr_state == "closed":
        message = f"❌ MR fechada no {project_name}: {mr_title}"
    else:
        message = f"🔄 MR atualizada no {project_name}: {mr_title}"
    
    await send_whatsapp_notification(message)
    
    return {"status": "processed", "message": message}

async def handle_push_event(payload: dict):
    """Processa eventos de push"""
    project_name = payload.get("project_name")
    commit_message = payload.get("commit_message")
    branch = payload.get("branch")
    
    message = f"📤 Push no {project_name} ({branch}): {commit_message}"
    
    await send_whatsapp_notification(message)
    
    return {"status": "processed", "message": message}
```

## Teste do Webhook

### 1. Teste Manual no GitLab

1. Vá para **Settings** > **Webhooks**
2. Clique em **Test** > **Push events**
3. Verifique se a ARIA recebeu a notificação

### 2. Teste via API

```bash
curl -X POST https://api.ar-online.com.br/webhook/gitlab/aria \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dtransforma2026" \
  -d '{
    "event_type": "pipeline",
    "project_name": "aria-sdr",
    "pipeline_status": "success",
    "aria_action": "pipeline_notification"
  }'
```

### 3. Teste de Notificação WhatsApp

```python
async def send_whatsapp_notification(message: str):
    """Envia notificação via WhatsApp"""
    whatsapp_data = {
        "to": "+5516997918658",
        "message": f"🤖 ARIA Notification:\n{message}",
        "source": "gitlab_webhook"
    }
    
    # Enviar via Mindchat API
    response = requests.post(
        "https://api-aronline.mindchatapp.com.br/webhook/whatsapp",
        json=whatsapp_data,
        headers={"Authorization": f"Bearer {MINDCHAT_API_TOKEN}"}
    )
    
    return response.json()
```

## Configuração de Filtros

### Filtro por Branch

- **Padrão**: `main`, `develop`
- **Regex**: `^(main|develop|release/.*)$`

### Filtro por Evento

- **Pipeline**: Apenas sucesso/falha
- **Deploy**: Apenas produção/staging
- **MR**: Apenas abertas/mergeadas

## Monitoramento

### Logs de Webhook

```python
import logging

logger = logging.getLogger("aria_webhook")

@app.post("/webhook/gitlab/aria")
async def gitlab_webhook(request: Request, payload: dict):
    logger.info(f"Webhook recebido: {payload.get('aria_action')}")
    
    try:
        result = await process_webhook(payload)
        logger.info(f"Webhook processado: {result}")
        return result
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Métricas

- **Webhooks recebidos**: Contador por tipo
- **Webhooks processados**: Taxa de sucesso
- **Notificações enviadas**: Via WhatsApp
- **Tempo de resposta**: Latência do endpoint

---

**ARIA-SDR** - Integração completa com GitLab Webhooks 🤖🔗
