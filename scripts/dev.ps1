param(
  [Parameter(Position=0)][string]$Command = "help"
)

switch ($Command) {
  "up"       { docker compose --profile dev up --build; break }
  "down"     { docker compose down -v; break }
  "rebuild"  { docker compose build --no-cache; break }
  "logs"     { docker compose logs -f; break }

  "run"      { uvicorn main:app --host 0.0.0.0 --port 8000; break }
  "run-dev"  { uvicorn main:app --host 0.0.0.0 --port 8000 --reload; break }

  "lint"     { ruff check . --fix; break }
  "fmt"      { black .; break }
  "type"     { pyright; break }
  "test"     { pytest -q; break }
  "smoke"    { pytest -q tests/test_smoke_api.py; break }

  "set-env"  {
    Write-Output "Exporting example env vars to current session..."
    $env:FASTAPI_BEARER_TOKEN = "realizati"
    $env:SUPABASE_URL = "https://<your>.supabase.co"
    $env:SUPABASE_SERVICE_ROLE_KEY = "<service-role>"
    $env:OPENAI_API_KEY = "<openai-key>"
    Write-Output "Done."
    break
  }

  "clean"    {
    Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Directory -Filter ".pytest_cache" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    break
  }

  Default     {
    Write-Output "Usage: .\scripts\dev.ps1 <command>"
    Write-Output "Commands: up, down, rebuild, logs, run, run-dev, lint, fmt, type, test, smoke, set-env, clean"
  }
}
