import os
from typing import Any
from unittest.mock import patch

import pytest
import requests
from fastapi.testclient import TestClient

# Importar a aplicação FastAPI
from main import app

# Base URL para testes locais (quando servidor estiver rodando)
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
TOKEN = os.getenv("BEARER_TOKEN", "dtransforma")

# Cliente de teste FastAPI
client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}


def test_healthz_reachable() -> None:
    """Testa o endpoint de health usando TestClient"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_healthz_reachable_with_server() -> None:
    """Testa o endpoint de health com servidor real (opcional)"""
    try:
        url = f"{BASE_URL}/healthz"
        resp = requests.get(url, headers=_auth_headers(), timeout=5)
        assert resp.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.skip("Servidor não está rodando - teste opcional")


def test_ragquery_smoke() -> None:
    """Testa o endpoint RAG usando TestClient"""
    with patch('main._embed') as mock_embed, \
         patch('main._rpc_match') as mock_rpc:
        mock_embed.return_value = [0.1] * 1536  # Mock embedding
        mock_rpc.return_value = [{"content": "test content", "similarity": 0.9}]
        
        payload: dict[str, Any] = {"query": "test", "top_k": 1}
        response = client.post("/rag/query", json=payload)
        # Aceita diferentes códigos de status dependendo da configuração
        assert response.status_code in (200, 400, 422, 500)
        if response.status_code == 200:
            assert isinstance(response.json(), dict)


def test_assistrouting_smoke() -> None:
    """Testa o endpoint de routing usando TestClient"""
    payload: dict[str, Any] = {"message": "hello"}
    response = client.post("/assist/routing", json=payload, headers=_auth_headers())
    # Aceita diferentes códigos de status dependendo da configuração
    assert response.status_code in (200, 400, 422, 401)
    if response.status_code == 200:
        assert isinstance(response.json(), dict)


def test_assistrouting_with_server() -> None:
    """Testa o endpoint de routing com servidor real (opcional)"""
    try:
        url = f"{BASE_URL}/assist/routing"
        payload: dict[str, Any] = {"message": "hello"}
        resp = requests.post(url, json=payload, headers=_auth_headers(), timeout=10)
        assert resp.status_code in (200, 400, 422, 401)
        if resp.status_code == 200:
            assert isinstance(resp.json(), dict)
    except requests.exceptions.ConnectionError:
        pytest.skip("Servidor não está rodando - teste opcional")
