# Script simplificado para iniciar o servidor ARIA-SDR
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ARIA-SDR - Iniciando Servidor" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Verificar se .env existe
if (-not (Test-Path ".env")) {
    Write-Host "[ERRO] Arquivo .env não encontrado!" -ForegroundColor Red
    Write-Host "Criando arquivo .env..." -ForegroundColor Yellow
    Copy-Item "config.env.example" ".env" -ErrorAction SilentlyContinue
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.local" ".env" -ErrorAction SilentlyContinue
    }
}

# Ativar ambiente virtual se existir
if (Test-Path "agno_env\Scripts\Activate.ps1") {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
    & "agno_env\Scripts\Activate.ps1"
} else {
    Write-Host "[AVISO] Ambiente virtual não encontrado" -ForegroundColor Yellow
    Write-Host "Usando Python global..." -ForegroundColor Gray
}

# Verificar Python
Write-Host "`nVerificando Python..." -ForegroundColor Yellow
python --version

# Instalar dependências se necessário
Write-Host "`nVerificando dependências..." -ForegroundColor Yellow
pip install fastapi uvicorn python-dotenv openai requests --quiet --disable-pip-version-check 2>$null

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Iniciando Servidor ARIA-SDR" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "API disponível em:" -ForegroundColor Green
Write-Host "  http://localhost:7777" -ForegroundColor White
Write-Host "  http://localhost:7777/docs" -ForegroundColor White
Write-Host "  http://localhost:7777/healthz" -ForegroundColor White
Write-Host "`nPressione Ctrl+C para parar`n" -ForegroundColor Yellow

# Iniciar servidor
python main.py

