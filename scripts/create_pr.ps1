Param(
  [string]$Base = "main",
  [string]$Head = "",
  [string]$Title = "",
  [string]$Body = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $env:GH_TOKEN -and -not $env:GITHUB_TOKEN) {
  Write-Error "Defina GH_TOKEN (ou GITHUB_TOKEN) com escopo repo para criar o PR."
}

# Descobre owner/repo a partir do remote origin
$remote = (git remote get-url origin)
if ($remote -match 'github.com[:/](?<owner>[^/]+)/(?<repo>[^/.]+)') {
  $owner = $Matches['owner']
  $repo = $Matches['repo']
} else {
  throw "Não foi possível extrair owner/repo do remote: $remote"
}

# Descobre branch atual
if (-not $Head) {
  $Head = (git rev-parse --abbrev-ref HEAD)
}

if (-not $Title) {
  $Title = "security(auth), test, ci: reforça auth, padroniza BASE_URL e sobe API no CI"
}

if (-not $Body) {
  $Body = @"
- Auth
  - Remove default “realizati” do bearer.
  - `require_bearer` usa `FASTAPI_BEARER_TOKEN` (fallback opcional a `BEARER_TOKEN`) e falha se não configurado.
  - `config.env.example`: placeholders vazios.

- Testes
  - `tests/test_smoke_api.py`: default `BASE_URL=http://127.0.0.1:8000`.
  - `tests/README.md`: docs atualizadas (preferir 127.0.0.1 no Windows).

- CI
  - `.github/workflows/ci.yml`: define `FASTAPI_BEARER_TOKEN` e `BASE_URL`, inicia `uvicorn` e aguarda `/healthz`.
  - Remove `|| true` para falhar se testes quebrarem.
  - Limpa diretórios `.github` aninhados duplicados.

- Validação
  - 7 testes passando localmente com servidor em 127.0.0.1:8000.
"@
}

$token = if ($env:GH_TOKEN) { $env:GH_TOKEN } else { $env:GITHUB_TOKEN }
$uri = "https://api.github.com/repos/$owner/$repo/pulls"
$payload = @{ title = $Title; head = $Head; base = $Base; body = $Body } | ConvertTo-Json -Depth 5

$headers = @{ Authorization = "token $token"; 'User-Agent' = 'create-pr-script' }

Write-Host "Criando PR: $owner/$repo $Head -> $Base"
$resp = Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -Body $payload -ContentType 'application/json'
Write-Host "PR criado: $($resp.html_url)"
