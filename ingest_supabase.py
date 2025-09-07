import os
from typing import Any

import requests

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()

if not SUPABASE_URL or not SUPABASE_KEY:
    raise SystemExit("Defina SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY no ambiente.")

HEADERS_JSON: dict[str, str] = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def ingest_rows(rows: list[dict[str, Any]]) -> requests.Response:
    url = f"{SUPABASE_URL}/rest/v1/aria_chunks"
    resp = requests.post(url, headers=HEADERS_JSON, json=rows, timeout=30)
    resp.raise_for_status()
    return resp


if __name__ == "__main__":
    # Exemplo mínimo de ingestão: ajuste os dados conforme necessário
    rows = [
        {
            "source": "faq",
            "doc_id": "faq_v1",
            "chunk_index": 0,
            "content": "Como funciona a AR Online...",
            "metadata": {"lang": "pt-BR"},
            # 'embedding' deve ser um vetor de floats gerado previamente
        }
    ]
    r = ingest_rows(rows)
    print(r.status_code, r.json())
