# Script de Configuração da API OpenAI
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARIA-SDR - Configuração OpenAI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Configurar variável de ambiente
$OPENAI_KEY = $env:OPENAI_API_KEY  # Use a variável de ambiente
$env:OPENAI_API_KEY = $OPENAI_KEY

Write-Host "`n[*] Testando conexão com OpenAI..." -ForegroundColor Yellow

# Testar conexão
python -c @"
import os
os.environ['OPENAI_API_KEY'] = '$OPENAI_KEY'

try:
    from openai import OpenAI
    client = OpenAI(api_key='$OPENAI_KEY')
    
    # Testar com um modelo simples
    response = client.models.list()
    print('[OK] Conexão com OpenAI bem-sucedida!')
    print('[INFO] Chave de API configurada e validada')
    
except Exception as e:
    print(f'[ERRO] Falha ao conectar: {e}')
    exit(1)
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[OK] OpenAI configurado com sucesso!" -ForegroundColor Green
    Write-Host "`nPróximos passos:" -ForegroundColor Cyan
    Write-Host "  1. A chave OpenAI está configurada" -ForegroundColor White
    Write-Host "  2. Reinicie o servidor ARIA-SDR para aplicar" -ForegroundColor White
    Write-Host "  3. Teste os endpoints de IA" -ForegroundColor White
    
    Write-Host "`n[INFO] Adicionando ao arquivo .env..." -ForegroundColor Yellow
    
    # Criar/atualizar .env
    $envContent = @"
# OpenAI Configuration
OPENAI_API_KEY=$OPENAI_KEY
ASSISTANT_ID=asst_Y9PUGUtEqgQWhg1WSkgPPzt6
ASSISTANT_TIMEOUT_SECONDS=12
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536

# API Configuration  
API_HOST=localhost
API_PORT=8000
API_DEBUG=false
FASTAPI_BEARER_TOKEN=dtransforma2026

# RAG Configuration
RAG_ENABLE=true
RAG_ENDPOINT=http://127.0.0.1:8000/rag/query
RAG_DEFAULT_SOURCE=faq
RAG_BACKEND=rpc

# Server Configuration
HOST=localhost
PORT=7777
"@
    
    $envContent | Out-File -FilePath ".env.generated" -Encoding UTF8
    Write-Host "[OK] Configuração salva em .env.generated" -ForegroundColor Green
    Write-Host "[INFO] Copie este arquivo para .env se necessário" -ForegroundColor Yellow
    
} else {
    Write-Host "`n[ERRO] Falha na configuração" -ForegroundColor Red
}

