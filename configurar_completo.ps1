# Script de Configuração Completa - ARIA-SDR
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARIA-SDR - Configuração Completa" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Configurações
$OPENAI_KEY = $env:OPENAI_API_KEY  # Use a variável de ambiente ao invés de hardcode
$SUPABASE_URL = "https://nywykslatlripxpiehfb.supabase.co"
$SUPABASE_PASSWORD = "2020*RealizaTI"

Write-Host "`n📝 Criando arquivo .env.local..." -ForegroundColor Yellow

$envContent = @"
# ============================================
# ARIA-SDR - Environment Configuration
# ============================================

# --- OpenAI Configuration ---
OPENAI_API_KEY=$OPENAI_KEY
ASSISTANT_ID=asst_Y9PUGUtEqgQWhg1WSkgPPzt6
ASSISTANT_TIMEOUT_SECONDS=12
CHAT_MODEL=gpt-4o-mini

# --- Supabase Configuration (API REST) ---
SUPABASE_URL=$SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY=PENDENTE_OBTER_NO_DASHBOARD
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536

# --- Supabase Database (Conexão Direta - Opcional) ---
SUPABASE_HOST=db.nywykslatlripxpiehfb.supabase.co
SUPABASE_PORT=5432
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=$SUPABASE_PASSWORD
DATABASE_URL=postgresql://postgres:$SUPABASE_PASSWORD@db.nywykslatlripxpiehfb.supabase.co:5432/postgres

# --- RAG Configuration ---
RAG_ENABLE=true
RAG_ENDPOINT=http://127.0.0.1:8000/rag/query
RAG_DEFAULT_SOURCE=faq
RAG_BACKEND=rpc

# --- API Configuration ---
API_HOST=localhost
API_PORT=8000
API_LOG_LEVEL=info
API_DEBUG=false
FASTAPI_BEARER_TOKEN=dtransforma2026
BEARER_TOKEN=dtransforma2026

# --- Server Configuration ---
HOST=localhost
PORT=7777

# --- Business Rules ---
VOLUME_ALTO_LIMIAR=1200

# --- GitLab Webhook ---
GITLAB_WEBHOOK_TOKEN=dtransforma2026
WHATSAPP_NUMBER=+5516997918658

# --- Mindchat Integration (Opcional) ---
MINDCHAT_API_TOKEN=your_mindchat_api_token_here
MINDCHAT_API_BASE_URL=https://api-aronline.mindchatapp.com.br
MINDCHAT_WEBHOOK_SECRET=your_webhook_secret
MINDCHAT_VERIFY_TOKEN=aria_verify_token

# --- Environment ---
APP_ENV=development
"@

$envContent | Out-File -FilePath ".env.local" -Encoding UTF8 -NoNewline

Write-Host "[✅] Arquivo .env.local criado!" -ForegroundColor Green

Write-Host "`n🧪 Testando OpenAI..." -ForegroundColor Yellow
$env:OPENAI_API_KEY = $OPENAI_KEY

python -c @"
from openai import OpenAI
client = OpenAI()
try:
    models = client.models.list()
    print('[✅] OpenAI: Conectado! {} modelos disponíveis'.format(len(list(models.data))))
except Exception as e:
    print('[❌] OpenAI: Erro -', str(e))
"@

Write-Host "`n📊 Status da Configuração:" -ForegroundColor Cyan
Write-Host "  [✅] OpenAI API Key configurada" -ForegroundColor Green
Write-Host "  [✅] Supabase URL configurada" -ForegroundColor Green
Write-Host "  [⚠️ ] Supabase Service Role Key - PENDENTE" -ForegroundColor Yellow
Write-Host "  [✅] Variáveis de ambiente criadas" -ForegroundColor Green

Write-Host "`n📝 Próximos Passos:" -ForegroundColor Cyan
Write-Host "  1. Obtenha a Service Role Key do Supabase:" -ForegroundColor White
Write-Host "     https://supabase.com/dashboard/project/nywykslatlripxpiehfb/settings/api" -ForegroundColor DarkGray
Write-Host "  2. Copie .env.local para .env e adicione a Service Role Key" -ForegroundColor White
Write-Host "  3. Execute: python setup_supabase.py (para criar as tabelas)" -ForegroundColor White
Write-Host "  4. Reinicie o servidor: Ctrl+C e execute novamente" -ForegroundColor White

Write-Host "`n🚀 Comandos úteis:" -ForegroundColor Cyan
Write-Host "  • Copiar configuração: Copy-Item .env.local .env" -ForegroundColor White
Write-Host "  • Ver configuração: Get-Content .env.local" -ForegroundColor White
Write-Host "  • Iniciar servidor: python main.py" -ForegroundColor White
Write-Host "  • Testar API: Invoke-WebRequest http://localhost:7777/healthz" -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Configuração concluída!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

