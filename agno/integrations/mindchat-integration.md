# Integração Mindchat - ARIA-SDR

## Visão Geral

O ARIA-SDR agora integra com a plataforma de atendimento **Mindchat** da AR Online, permitindo:

- Gestão de tickets de atendimento
- Integração com chat em tempo real
- Analytics de atendimento
- Gestão de clientes

## Configuração

### Variáveis de Ambiente

```bash
# Mindchat API Configuration
MINDCHAT_API_TOKEN=c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58
MINDCHAT_API_BASE_URL=https://api-aronline.mindchatapp.com.br
MINDCHAT_API_DOCS=https://api-aronline.mindchatapp.com.br/api-docs/
```

## Endpoints Disponíveis

### Tickets
- `GET /api/tickets` - Listar tickets
- `POST /api/tickets` - Criar novo ticket
- `GET /api/tickets/{id}` - Obter ticket específico
- `PUT /api/tickets/{id}` - Atualizar ticket

### Mensagens
- `GET /api/messages` - Listar mensagens
- `POST /api/messages` - Enviar mensagem
- `GET /api/messages/{id}` - Obter mensagem específica

### Clientes
- `GET /api/customers` - Listar clientes
- `POST /api/customers` - Criar novo cliente
- `GET /api/customers/{id}` - Obter cliente específico
- `PUT /api/customers/{id}` - Atualizar cliente

### Analytics
- `GET /api/analytics` - Obter métricas de atendimento
- `GET /api/analytics/tickets` - Analytics de tickets
- `GET /api/analytics/messages` - Analytics de mensagens

## Autenticação

Todas as requisições para a API do Mindchat devem incluir o token de autenticação:

```bash
Authorization: Bearer c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58
```

## Integração com ARIA-SDR

### Fluxo de Atendimento

1. **Cliente inicia conversa** → Agno
2. **Agno processa** → FastAPI
3. **FastAPI analisa** → OpenAI Assistant + RAG
4. **Se necessário escalar** → Mindchat API
5. **Ticket criado** → Cliente atendido

### Casos de Uso

- **Volume alto** → Criar ticket no Mindchat
- **Questão complexa** → Escalar para atendente humano
- **Follow-up** → Integrar com sistema de tickets
- **Analytics** → Métricas de atendimento

## Documentação Completa

Para mais detalhes sobre a API do Mindchat, consulte:
**[https://api-aronline.mindchatapp.com.br/api-docs/](https://api-aronline.mindchatapp.com.br/api-docs/)**

## Exemplo de Uso

```python
import requests
import os

# Configuração
MINDCHAT_API_TOKEN = os.getenv("MINDCHAT_API_TOKEN")
MINDCHAT_API_BASE_URL = os.getenv("MINDCHAT_API_BASE_URL")

# Headers
headers = {
    "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
    "Content-Type": "application/json"
}

# Criar ticket
def create_ticket(customer_id, subject, message):
    url = f"{MINDCHAT_API_BASE_URL}/api/tickets"
    payload = {
        "customer_id": customer_id,
        "subject": subject,
        "message": message,
        "priority": "medium"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Listar tickets
def list_tickets():
    url = f"{MINDCHAT_API_BASE_URL}/api/tickets"
    response = requests.get(url, headers=headers)
    return response.json()
```
