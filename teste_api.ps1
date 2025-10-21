# Script de Teste da API ARIA-SDR
# Execute este script quando o servidor estiver rodando

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ARIA-SDR - Testes da API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:7777"
$token = "dtransforma2026"

Write-Host "Base URL: $baseUrl" -ForegroundColor Gray
Write-Host "Token: $token" -ForegroundColor Gray
Write-Host ""

# Função para fazer requisições
function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Endpoint,
        [string]$Description,
        [hashtable]$Body = $null,
        [bool]$RequiresAuth = $false
    )
    
    Write-Host "Testando: $Description" -ForegroundColor Yellow
    Write-Host "  $Method $Endpoint" -ForegroundColor Gray
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        if ($RequiresAuth) {
            $headers["Authorization"] = "Bearer $token"
        }
        
        $params = @{
            Uri = "$baseUrl$Endpoint"
            Method = $Method
            Headers = $headers
            TimeoutSec = 30
        }
        
        if ($Body) {
            $params["Body"] = ($Body | ConvertTo-Json -Depth 10)
        }
        
        $response = Invoke-RestMethod @params
        Write-Host "  ✅ Sucesso!" -ForegroundColor Green
        Write-Host "  Resposta:" -ForegroundColor Gray
        $response | ConvertTo-Json -Depth 5 | Write-Host
        Write-Host ""
        return $true
    }
    catch {
        Write-Host "  ❌ Erro: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        return $false
    }
}

# Contador de testes
$totalTests = 0
$passedTests = 0

# Teste 1: Health Check
$totalTests++
Write-Host "-----------------------------------" -ForegroundColor Cyan
Write-Host "Teste 1/5: Health Check" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
if (Test-Endpoint -Method "GET" -Endpoint "/healthz" -Description "Health Check") {
    $passedTests++
}

# Teste 2: Auth Debug
$totalTests++
Write-Host "-----------------------------------" -ForegroundColor Cyan
Write-Host "Teste 2/5: Autenticação" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
if (Test-Endpoint -Method "GET" -Endpoint "/auth_debug" -Description "Debug de Autenticação" -RequiresAuth $true) {
    $passedTests++
}

# Teste 3: Assist Routing - Pergunta simples
$totalTests++
Write-Host "-----------------------------------" -ForegroundColor Cyan
Write-Host "Teste 3/5: Routing - Pergunta Simples" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
$body1 = @{
    message = "Olá, como você pode me ajudar?"
}
if (Test-Endpoint -Method "POST" -Endpoint "/assist/routing" -Description "Pergunta simples" -Body $body1 -RequiresAuth $true) {
    $passedTests++
}

# Teste 4: Assist Routing - Envio baixo volume
$totalTests++
Write-Host "-----------------------------------" -ForegroundColor Cyan
Write-Host "Teste 4/5: Routing - Envio Baixo Volume" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
$body2 = @{
    message = "Preciso enviar 300 mensagens por mês"
    variables = @{
        lead_volumetria = "300"
    }
}
if (Test-Endpoint -Method "POST" -Endpoint "/assist/routing" -Description "Envio baixo volume" -Body $body2 -RequiresAuth $true) {
    $passedTests++
}

# Teste 5: Assist Routing - Envio alto volume
$totalTests++
Write-Host "-----------------------------------" -ForegroundColor Cyan
Write-Host "Teste 5/5: Routing - Envio Alto Volume" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
$body3 = @{
    message = "Quero fazer envio em massa de 5000 mensagens"
    variables = @{
        lead_volumetria = "5000"
    }
}
if (Test-Endpoint -Method "POST" -Endpoint "/assist/routing" -Description "Envio alto volume" -Body $body3 -RequiresAuth $true) {
    $passedTests++
}

# Resumo
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Resumo dos Testes" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total de testes: $totalTests" -ForegroundColor White
Write-Host "Testes passados: $passedTests" -ForegroundColor Green
Write-Host "Testes falhados: $($totalTests - $passedTests)" -ForegroundColor Red
Write-Host ""

$percentage = [math]::Round(($passedTests / $totalTests) * 100, 2)
Write-Host "Taxa de sucesso: $percentage%" -ForegroundColor $(if ($percentage -eq 100) { "Green" } elseif ($percentage -ge 80) { "Yellow" } else { "Red" })
Write-Host ""

if ($passedTests -eq $totalTests) {
    Write-Host "🎉 Todos os testes passaram! A API está funcionando perfeitamente." -ForegroundColor Green
} elseif ($passedTests -gt 0) {
    Write-Host "⚠️ Alguns testes falharam. Verifique a configuração e os logs." -ForegroundColor Yellow
} else {
    Write-Host "❌ Todos os testes falharam. Verifique se o servidor está rodando." -ForegroundColor Red
    Write-Host "Execute: .\teste_local.ps1" -ForegroundColor White
}

Write-Host ""

