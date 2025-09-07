import os
from typing import Any

import requests

# Base URL for the running API, e.g. http://localhost:8000
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
TOKEN = os.getenv("BEARER_TOKEN", "realizati")


def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}


def test_healthz_reachable() -> None:
    url = f"{BASE_URL}/healthz"
    resp = requests.get(url, headers=_auth_headers(), timeout=10)
    assert resp.status_code == 200


def test_ragquery_smoke() -> None:
    url = f"{BASE_URL}/rag/query"
    payload: dict[str, Any] = {"query": "test", "top_k": 1}
    resp = requests.post(url, json=payload, headers=_auth_headers(), timeout=20)
    assert resp.status_code in (200, 400, 422)
    if resp.status_code == 200:
        assert isinstance(resp.json(), dict)


def test_assistrouting_smoke() -> None:
    url = f"{BASE_URL}/assist/routing"
    payload: dict[str, Any] = {"message": "hello"}
    resp = requests.post(url, json=payload, headers=_auth_headers(), timeout=20)
    assert resp.status_code in (200, 400, 422)
    if resp.status_code == 200:
        assert isinstance(resp.json(), dict)
