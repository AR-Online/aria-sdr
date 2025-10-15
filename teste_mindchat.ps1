# Script PowerShell para Testes Mindchat ARIA-SDR
# Execute: .\teste_mindchat.ps1

Write-Host "🚀 TESTES MANUAIS - INTEGRAÇÃO MINDCHAT ARIA-SDR" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Yellow

$baseUrl = "http://localhost:8000"

# Função para mostrar resultado
function Show-Result {
    param($TestName, $Success, $Details = "")
    
    if ($Success) {
        Write-Host "✅ PASSOU $TestName" -ForegroundColor Green
    } else {
        Write-Host "❌ FALHOU $TestName" -ForegroundColor Red
    }
    
    if ($Details) {
        Write-Host "   $Details" -ForegroundColor Gray
    }
}

# Teste 1: Health Check
Write-Host "`n🧪 TESTE 1: Health Check" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/mindchat/health" -Method GET
    Show-Result "Health Check" $true "Status: $($response.status)"
    $healthOk = $true
} catch {
    Show-Result "Health Check" $false "Erro: $($_.Exception.Message)"
    $healthOk = $false
}

# Teste 2: Verificação de Webhook
Write-Host "`n🧪 TESTE 2: Verificação de Webhook" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Yellow

try {
    $params = @{
        hub_mode = "subscribe"
        hub_challenge = "teste_powershell_123"
        hub_verify_token = "aria_verify_token"
    }
    
    $response = Invoke-RestMethod -Uri "$baseUrl/mindchat/webhook/verify" -Method GET -Body $params
    if ($response -like "*teste_powershell_123*") {
        Show-Result "Verificação de Webhook" $true "Token verificado com sucesso"
        $webhookOk = $true
    } else {
        Show-Result "Verificação de Webhook" $false "Resposta inesperada"
        $webhookOk = $false
    }
} catch {
    Show-Result "Verificação de Webhook" $false "Erro: $($_.Exception.Message)"
    $webhookOk = $false
}

# Teste 3: Envio de Mensagem
Write-Host "`n🧪 TESTE 3: Envio de Mensagem" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Yellow

try {
    $timestamp = Get-Date -Format "HH:mm:ss"
    $params = @{
        to = "5516999999999"
        message = "Teste PowerShell ARIA-SDR - $timestamp"
        message_type = "text"
    }
    
    $response = Invoke-RestMethod -Uri "$baseUrl/mindchat/send" -Method POST -Body $params
    Show-Result "Envio de Mensagem" $true "Status: $($response.status)"
    $sendOk = $true
} catch {
    Show-Result "Envio de Mensagem" $false "Erro: $($_.Exception.Message)"
    $sendOk = $false
}

# Teste 4: Lista de Mensagens
Write-Host "`n🧪 TESTE 4: Lista de Mensagens" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/mindchat/messages?page=1&page_size=3" -Method GET
    Show-Result "Lista de Mensagens" $true "Status: $($response.status)"
    $messagesOk = $true
} catch {
    Show-Result "Lista de Mensagens" $false "Erro: $($_.Exception.Message)"
    $messagesOk = $false
}

# Teste 5: Buscar Conversas
Write-Host "`n🧪 TESTE 5: Buscar Conversas" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/mindchat/conversations" -Method GET
    Show-Result "Buscar Conversas" $true "Status: $($response.status)"
    $conversationsOk = $true
} catch {
    Show-Result "Buscar Conversas" $false "Erro: $($_.Exception.Message)"
    $conversationsOk = $false
}

# Resumo Final
Write-Host "`n🎯 RESUMO DOS TESTES" -ForegroundColor Magenta
Write-Host "=" * 60 -ForegroundColor Yellow

$results = @($healthOk, $webhookOk, $sendOk, $messagesOk, $conversationsOk)
$passed = ($results | Where-Object { $_ -eq $true }).Count
$total = $results.Count

Write-Host "✅ PASSOU Health Check" -ForegroundColor $(if($healthOk) {"Green"} else {"Red"})
Write-Host "✅ PASSOU Verificação de Webhook" -ForegroundColor $(if($webhookOk) {"Green"} else {"Red"})
Write-Host "✅ PASSOU Envio de Mensagem" -ForegroundColor $(if($sendOk) {"Green"} else {"Red"})
Write-Host "✅ PASSOU Lista de Mensagens" -ForegroundColor $(if($messagesOk) {"Green"} else {"Red"})
Write-Host "✅ PASSOU Buscar Conversas" -ForegroundColor $(if($conversationsOk) {"Green"} else {"Red"})

Write-Host "`n🎯 RESULTADO FINAL: $passed/$total testes passaram" -ForegroundColor $(if($passed -eq $total) {"Green"} elseif($passed -ge ($total * 0.8)) {"Yellow"} else {"Red"})

if ($passed -eq $total) {
    Write-Host "🎉 TODOS OS TESTES PASSARAM! Integração funcionando perfeitamente!" -ForegroundColor Green
} elseif ($passed -ge ($total * 0.8)) {
    Write-Host "⚠️  Maioria dos testes passou. Verifique os que falharam." -ForegroundColor Yellow
} else {
    Write-Host "🚨 Muitos testes falharam. Verifique a configuração." -ForegroundColor Red
}

Write-Host "`n💡 Para mais detalhes, consulte: GUIA_TESTE_MINDCHAT.md" -ForegroundColor Cyan
Write-Host "🐍 Para teste Python: python teste_simples.py" -ForegroundColor Cyan
