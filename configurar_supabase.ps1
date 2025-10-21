# Script de Configuração do Supabase para ARIA-SDR
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARIA-SDR - Configuração do Supabase" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Solicitar senha
Write-Host "`nPor favor, forneça a senha do banco de dados:" -ForegroundColor Yellow
$password = Read-Host -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
$plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Configurar variáveis de ambiente temporárias
$env:SUPABASE_HOST = "db.nywykslatlripxpiehfb.supabase.co"
$env:SUPABASE_PORT = "5432"
$env:SUPABASE_DATABASE = "postgres"
$env:SUPABASE_USER = "postgres"
$env:SUPABASE_PASSWORD = $plainPassword
$env:SUPABASE_URL = "https://nywykslatlripxpiehfb.supabase.co"

# Connection string para PostgreSQL
$DATABASE_URL = "postgresql://postgres:$plainPassword@db.nywykslatlripxpiehfb.supabase.co:5432/postgres"
$env:DATABASE_URL = $DATABASE_URL

Write-Host "`n[*] Testando conexão com Supabase..." -ForegroundColor Yellow

# Executar script de setup
python setup_supabase.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[OK] Configuração concluída com sucesso!" -ForegroundColor Green
    Write-Host "`nPróximos passos:" -ForegroundColor Cyan
    Write-Host "  1. O banco de dados está configurado" -ForegroundColor White
    Write-Host "  2. Adicione a senha no arquivo .env manualmente" -ForegroundColor White
    Write-Host "  3. Reinicie o servidor ARIA-SDR" -ForegroundColor White
} else {
    Write-Host "`n[ERRO] Falha na configuração" -ForegroundColor Red
    Write-Host "Verifique as credenciais e tente novamente" -ForegroundColor Yellow
}

