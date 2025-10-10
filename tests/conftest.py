import os
import pytest
from unittest.mock import patch, MagicMock

# Mock das variáveis de ambiente para testes
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        'FASTAPI_BEARER_TOKEN': 'test-token',
        'OPENAI_API_KEY': 'test-openai-key',
        'ASSISTANT_ID': 'test-assistant-id',
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-supabase-key',
        'CLOUDFLARE_API_TOKEN': 'test-cloudflare-key',
        'MINDCHAT_API_TOKEN': 'test-mindchat-key',
        'MINDCHAT_API_BASE_URL': 'https://test.mindchat.com',
        'MINDCHAT_API_DOCS': 'https://test.mindchat.com/docs',
        'API_HOST': '0.0.0.0',
        'API_PORT': '8000',
        'API_LOG_LEVEL': 'info',
        'ASSISTANT_TIMEOUT_SECONDS': '12',
        'EMBEDDING_MODEL': 'text-embedding-3-small',
        'EMBEDDING_DIM': '1536',
        'RAG_ENABLE': 'true',
        'RAG_ENDPOINT': 'http://127.0.0.1:8000/rag/query',
        'RAG_DEFAULT_SOURCE': 'faq',
        'VOLUME_ALTO_LIMIAR': '1200',
        'AGNO_ROUTING_WEBHOOK': 'https://agno.ar-infra.com.br/webhook/assist/routing',
        'AGNO_API_BASE_URL': 'https://agno.ar-infra.com.br/api/v1',
    }):
        yield

# Mock do OpenAI client para testes
@pytest.fixture
def mock_openai_client():
    with patch('main.client_assistant') as mock_client:
        mock_client.beta.threads.create.return_value.id = 'test-thread-id'
        mock_client.beta.threads.messages.create.return_value = MagicMock()
        mock_client.beta.threads.runs.create.return_value.id = 'test-run-id'
        yield mock_client

# Mock das requisições HTTP para testes
@pytest.fixture
def mock_requests():
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'ok'}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'status': 'ok'}
        yield mock_post, mock_get