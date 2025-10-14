# ARIA-SDR - AgentOS Startup Script (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARIA-SDR - AgentOS Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Ativar ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
& "agno_env\Scripts\Activate.ps1"

# Verificar se o ambiente foi ativado
Write-Host "Verificando Python path..." -ForegroundColor Yellow
python -c "import sys; print('Python path:', sys.executable)"

# Verificar versão do OpenAI
Write-Host "Verificando versão do OpenAI..." -ForegroundColor Yellow
python -c "import openai; print('OpenAI version:', openai.__version__)"

# Executar AgentOS
Write-Host ""
Write-Host "Iniciando AgentOS..." -ForegroundColor Green
python aria_first_os.py
