# Script de Teste Local ARIA-SDR
# Execute este script para testar a aplicação localmente

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ARIA-SDR - Teste Local Manual" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se o ambiente virtual existe
if (Test-Path "agno_env\Scripts\Activate.ps1") {
    Write-Host "[OK] Ambiente virtual encontrado" -ForegroundColor Green
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
    & "agno_env\Scripts\Activate.ps1"
} else {
    Write-Host "[ERRO] Ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host "Execute primeiro: python -m venv agno_env" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# 2. Verificar Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Python não encontrado!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python instalado" -ForegroundColor Green
Write-Host ""

# 3. Verificar arquivo .env
if (Test-Path ".env") {
    Write-Host "[OK] Arquivo .env encontrado" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Arquivo .env não encontrado!" -ForegroundColor Yellow
    Write-Host "Criando .env a partir do config.env.example..." -ForegroundColor Yellow
    Copy-Item "config.env.example" ".env"
}

# 4. Verificar chave OpenAI
Write-Host ""
Write-Host "Verificando configuração OpenAI..." -ForegroundColor Yellow
$env_content = Get-Content ".env" -Raw
if ($env_content -match "OPENAI_API_KEY=sk-") {
    Write-Host "[OK] Chave OpenAI configurada" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Configure sua OPENAI_API_KEY no arquivo .env" -ForegroundColor Yellow
    Write-Host "Edite o arquivo .env e adicione sua chave da OpenAI" -ForegroundColor Yellow
}

Write-Host ""

# 5. Instalar/Verificar dependências
Write-Host "Verificando dependências..." -ForegroundColor Yellow
Write-Host "Instalando dependências necessárias..." -ForegroundColor Yellow
pip install --quiet --upgrade pip 2>&1 | Out-Null
pip install --quiet -r requirements.txt 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Dependências instaladas" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Erro ao instalar dependências" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Iniciando Servidor ARIA-SDR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API disponível em:" -ForegroundColor Green
Write-Host "  - http://localhost:7777" -ForegroundColor White
Write-Host "  - http://localhost:7777/docs (Swagger UI)" -ForegroundColor White
Write-Host "  - http://localhost:7777/healthz (Health Check)" -ForegroundColor White
Write-Host ""
Write-Host "Para testar, abra outro terminal e execute:" -ForegroundColor Yellow
Write-Host '  curl http://localhost:7777/healthz' -ForegroundColor White
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
Write-Host ""

# 6. Iniciar o servidor
python main.py

