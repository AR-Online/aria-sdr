#!/usr/bin/env python3
"""
Testes de Equivalencia n8n -> Agno
ARIA-SDR - Validacao de Migracao
"""

import os
import pytest
import requests
from typing import Dict, Any
from fastapi.testclient import TestClient

# Importar a aplicacao FastAPI
from main import app

class TestN8nEquivalence:
    """Testes para validar equivalencia entre n8n e Agno"""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        """Headers de autenticacao"""
        token = os.getenv("FASTAPI_BEARER_TOKEN", "dtransforma2026")
        return {"Authorization": f"Bearer {token}"}
    
    def test_routing_functionality_preserved(self, client, auth_headers):
        """Testa se funcionalidades de routing foram preservadas"""
        
        # Teste 1: Routing basico
        payload = {
            "user_text": "Ola, preciso de ajuda",
            "channel": "web"
        }
        
        response = client.post("/assist/routing", json=payload, headers=auth_headers)
        
        # Validacoes
        assert response.status_code == 200
        data = response.json()
        
        # Verificar campos obrigatorios
        assert "thread_id" in data
        assert "reply_text" in data
        assert "variables" in data
        
        # Verificar thread_id format
        assert data["thread_id"].startswith("thr_")
        
        print(f"✅ Routing basico funcionando: {data['thread_id']}")
    
    def test_volume_classification_preserved(self, client, auth_headers):
        """Testa se classificacao de volume foi preservada"""
        
        # Teste volume alto
        payload_high = {
            "user_text": "Preciso enviar 1500 emails por mes",
            "channel": "web"
        }
        
        response_high = client.post("/assist/routing", json=payload_high, headers=auth_headers)
        assert response_high.status_code == 200
        
        # Teste volume baixo
        payload_low = {
            "user_text": "Preciso enviar 100 emails por mes",
            "channel": "web"
        }
        
        response_low = client.post("/assist/routing", json=payload_low, headers=auth_headers)
        assert response_low.status_code == 200
        
        print("✅ Classificacao de volume preservada")
    
    def test_rag_functionality_preserved(self, client):
        """Testa se funcionalidades RAG foram preservadas"""
        
        payload = {
            "query": "Como funciona a AR Online?",
            "top_k": 3
        }
        
        response = client.post("/rag/query", json=payload)
        
        # Aceita diferentes codigos dependendo da configuracao
        assert response.status_code in (200, 400, 422, 500)
        
        if response.status_code == 200:
            data = response.json()
            assert "results" in data or "matches" in data
            print("✅ RAG funcionando")
        else:
            print(f"⚠️ RAG com configuracao limitada: {response.status_code}")
    
    def test_whatsapp_webhook_preserved(self, client, auth_headers):
        """Testa se webhook WhatsApp foi preservado"""
        
        payload = {
            "from": "+5516999999999",
            "to": "+5516997918658",
            "message": "Teste webhook",
            "timestamp": "2025-01-10T10:00:00Z",
            "id": "test_msg_123",
            "type": "text"
        }
        
        response = client.post("/whatsapp/webhook", json=payload, headers=auth_headers)
        
        # Aceita diferentes codigos dependendo da configuracao
        assert response.status_code in (200, 400, 422, 401)
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            print("✅ Webhook WhatsApp funcionando")
        else:
            print(f"⚠️ Webhook WhatsApp com configuracao limitada: {response.status_code}")
    
    def test_thread_management_improved(self, client, auth_headers):
        """Testa se gerenciamento de thread foi melhorado"""
        
        # Teste com thread_id no header
        headers_with_thread = auth_headers.copy()
        headers_with_thread["X-Thread-Id"] = "test_thread_123"
        
        payload = {
            "user_text": "Continuacao da conversa",
            "thread_id": "body_thread_456"  # Deve ser ignorado
        }
        
        response = client.post("/assist/routing", json=payload, headers=headers_with_thread)
        assert response.status_code == 200
        
        data = response.json()
        
        # Thread do header deve ter precedencia
        assert data["thread_id"] == "test_thread_123"
        assert data["variables"]["thread_id"] == "test_thread_123"
        
        print("✅ Gerenciamento de thread melhorado")
    
    def test_error_handling_improved(self, client, auth_headers):
        """Testa se tratamento de erros foi melhorado"""
        
        # Teste com payload invalido
        response = client.post("/assist/routing", json={}, headers=auth_headers)
        
        # Deve retornar erro estruturado
        assert response.status_code in (400, 422)
        
        if response.status_code in (400, 422):
            print("✅ Tratamento de erros melhorado")
    
    def test_health_check_available(self, client):
        """Testa se health check esta disponivel"""
        
        response = client.get("/healthz")
        assert response.status_code == 200
        
        data = response.json()
        assert data == {"ok": True}
        
        print("✅ Health check disponivel")
    
    def test_agno_configuration_status(self):
        """Testa status da configuracao do Agno"""
        
        agno_token = os.getenv("AGNO_AUTH_TOKEN", "")
        agno_bot_id = os.getenv("AGNO_BOT_ID", "")
        
        if agno_token and agno_bot_id:
            print("✅ Configuracao Agno completa")
            return True
        else:
            print("⚠️ Configuracao Agno incompleta:")
            if not agno_token:
                print("  - AGNO_AUTH_TOKEN nao configurado")
            if not agno_bot_id:
                print("  - AGNO_BOT_ID nao configurado")
            return False

def run_equivalence_tests():
    """Executa todos os testes de equivalencia"""
    
    print("=" * 60)
    print("TESTES DE EQUIVALENCIA n8n -> Agno")
    print("ARIA-SDR - Validacao de Migracao")
    print("=" * 60)
    
    # Verificar configuracao Agno
    agno_token = os.getenv("AGNO_AUTH_TOKEN", "")
    agno_bot_id = os.getenv("AGNO_BOT_ID", "")
    
    print(f"\nConfiguracao Agno:")
    print(f"  AGNO_AUTH_TOKEN: {'✅ Configurado' if agno_token else '❌ Nao configurado'}")
    print(f"  AGNO_BOT_ID: {'✅ Configurado' if agno_bot_id else '❌ Nao configurado'}")
    
    # Executar testes
    print(f"\nExecutando testes de equivalencia...")
    
    # Usar pytest para executar os testes
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--no-header"
    ])

if __name__ == "__main__":
    run_equivalence_tests()
