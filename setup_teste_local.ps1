# Script de Setup para Teste Local ARIA-SDR
# Este script prepara o ambiente para testes locais

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ARIA-SDR - Setup Teste Local" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Criar arquivo .env se não existir
if (-not (Test-Path ".env")) {
    Write-Host "Criando arquivo .env..." -ForegroundColor Yellow
    
    $envContent = @"
# ARIA-SDR - Configuração Local de Teste
# Criado automaticamente para teste local

# --- FastAPI / Auth ---
API_HOST=localhost
API_PORT=7777
API_LOG_LEVEL=info
API_DEBUG=true

# Token de autenticação
FASTAPI_BEARER_TOKEN=dtransforma2026
BEARER_TOKEN=dtransforma

# --- OpenAI (OBRIGATÓRIO) ---
# IMPORTANTE: Adicione sua chave da OpenAI aqui
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_API_KEY_HERE
ASSISTANT_ID=asst_Y9PUGUtEqgQWhg1WSkgPPzt6
ASSISTANT_TIMEOUT_SECONDS=12
CHAT_MODEL=gpt-4o-mini

# --- Supabase (RAG backend) - OPCIONAL para teste básico ---
SUPABASE_URL=https://nywykslatlripxpiehfb.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im55d3lrc2xhdGxyaXB4cGllaGZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTcxOTY2MjEsImV4cCI6MjA3Mjc3MjYyMX0.XpjP5oTbVu8MU87fE39zDrYR8zo98L1zOmiFIb3e8No
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im55d3lrc2xhdGxyaXB4cGllaGZiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzE5NjYyMSwiZXhwIjoyMDcyNzcyNjIxfQ.RCZsK_fizrwb-om-unYFCpsDV0sQ43FXWtAvnyIZlF4
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536

# --- RAG Configuration ---
RAG_ENABLE=false
RAG_ENDPOINT=http://127.0.0.1:7777/rag/query
RAG_DEFAULT_SOURCE=faq
RAG_BACKEND=rpc

# --- Business Rules ---
VOLUME_ALTO_LIMIAR=1200

# --- Ambiente ---
APP_ENV=development
HOST=localhost
PORT=7777

# --- GitLab Webhook (teste local) ---
GITLAB_WEBHOOK_TOKEN=dtransforma2026
WHATSAPP_NUMBER=+5516997918658

# --- Mindchat Integration (OPCIONAL para teste básico) ---
MINDCHAT_API_TOKEN=
MINDCHAT_API_BASE_URL=https://api-aronline.mindchatapp.com.br
MINDCHAT_WEBHOOK_SECRET=
MINDCHAT_VERIFY_TOKEN=aria_verify_token

# --- WhatsApp (OPCIONAL para teste básico) ---
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_VERIFY_TOKEN=

# --- Cloudflare (OPCIONAL) ---
CLOUDFLARE_API_TOKEN=
"@
    
    Set-Content -Path ".env" -Value $envContent
    Write-Host "[OK] Arquivo .env criado" -ForegroundColor Green
    Write-Host ""
    Write-Host "[IMPORTANTE] Edite o arquivo .env e adicione sua OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host "Comando: notepad .env" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "[OK] Arquivo .env já existe" -ForegroundColor Green
}

# 2. Verificar se ambiente virtual existe
if (-not (Test-Path "agno_env\Scripts\Activate.ps1")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv agno_env
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Ambiente virtual criado" -ForegroundColor Green
    } else {
        Write-Host "[ERRO] Falha ao criar ambiente virtual" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[OK] Ambiente virtual já existe" -ForegroundColor Green
}

Write-Host ""
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
& "agno_env\Scripts\Activate.ps1"

# 3. Instalar dependências
Write-Host ""
Write-Host "Instalando dependências..." -ForegroundColor Yellow
Write-Host "Isso pode levar alguns minutos..." -ForegroundColor Gray

# Atualizar pip
python -m pip install --upgrade pip --quiet

# Instalar dependências
pip install -r requirements.txt --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Dependências instaladas com sucesso" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Alguns pacotes podem ter falhado" -ForegroundColor Yellow
}

# 4. Verificar instalação
Write-Host ""
Write-Host "Verificando instalação..." -ForegroundColor Yellow

$packages = @("fastapi", "uvicorn", "openai", "requests", "python-dotenv")
$allOk = $true

foreach ($package in $packages) {
    $result = python -c "import $package; print('OK')" 2>&1
    if ($result -match "OK") {
        Write-Host "[OK] $package" -ForegroundColor Green
    } else {
        Write-Host "[ERRO] $package não instalado" -ForegroundColor Red
        $allOk = $false
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Setup Concluído!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($allOk) {
    Write-Host "✅ Tudo pronto para começar!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Yellow
    Write-Host "1. Edite o arquivo .env e adicione sua OPENAI_API_KEY" -ForegroundColor White
    Write-Host "   Comando: notepad .env" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Execute o servidor:" -ForegroundColor White
    Write-Host "   .\teste_local.ps1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Acesse a documentação:" -ForegroundColor White
    Write-Host "   http://localhost:7777/docs" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Consulte o guia completo: TESTE_LOCAL_GUIA.md" -ForegroundColor Cyan
} else {
    Write-Host "⚠️ Alguns pacotes falharam na instalação" -ForegroundColor Yellow
    Write-Host "Tente executar manualmente: pip install -r requirements.txt" -ForegroundColor White
}

Write-Host ""

