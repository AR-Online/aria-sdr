# Script PowerShell para configurar GitLab remote para ARIA-SDR

Write-Host "🚀 Configurando GitLab remote para ARIA-SDR..." -ForegroundColor Green

# Verificar se estamos em um repositório git
if (-not (Test-Path ".git")) {
    Write-Host "❌ Erro: Não estamos em um repositório git" -ForegroundColor Red
    exit 1
}

# Verificar remotes atuais
Write-Host "📋 Remotes atuais:" -ForegroundColor Yellow
git remote -v

Write-Host ""
Write-Host "📝 Para continuar, você precisa:" -ForegroundColor Cyan
Write-Host "1. Criar um projeto no GitLab" -ForegroundColor White
Write-Host "2. Obter a URL do repositório GitLab" -ForegroundColor White
Write-Host ""

# Solicitar informações do usuário
$GITLAB_USERNAME = Read-Host "Digite seu nome de usuário do GitLab"
$PROJECT_NAME = Read-Host "Digite o nome do projeto no GitLab (ex: aria-sdr)"

# Construir URL do GitLab
$GITLAB_URL = "https://gitlab.com/$GITLAB_USERNAME/$PROJECT_NAME.git"

Write-Host ""
Write-Host "🔗 URL do GitLab que será configurada: $GITLAB_URL" -ForegroundColor Yellow
Write-Host ""

# Confirmar configuração
$CONFIRM = Read-Host "Confirma a configuração? (y/n)"

if ($CONFIRM -eq "y" -or $CONFIRM -eq "Y") {
    Write-Host "⚙️  Configurando remote do GitLab..." -ForegroundColor Blue
    
    # Adicionar remote do GitLab
    git remote add gitlab $GITLAB_URL
    
    Write-Host "✅ Remote do GitLab adicionado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Remotes configurados:" -ForegroundColor Yellow
    git remote -v
    
    Write-Host ""
    Write-Host "🚀 Próximos passos:" -ForegroundColor Cyan
    Write-Host "1. Fazer push inicial: git push gitlab main" -ForegroundColor White
    Write-Host "2. Configurar sincronização: git remote set-url --add --push origin $GITLAB_URL" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Para fazer push para ambos os repositórios simultaneamente:" -ForegroundColor Magenta
    Write-Host "   git push origin main" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "❌ Configuração cancelada" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Configuração concluída!" -ForegroundColor Green
