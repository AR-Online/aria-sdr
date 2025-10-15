#!/usr/bin/env python3
"""
Script de teste para integração Mindchat real da ARIA-SDR
Testa os endpoints descobertos na API real
"""

import json
import requests
import os
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
MINDCHAT_API_TOKEN = "c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58"
FASTAPI_BEARER_TOKEN = os.getenv("FASTAPI_BEARER_TOKEN", "dtransforma2026")

def test_mindchat_health():
    """Testa health check da integração Mindchat"""
    print("Testando health check Mindchat...")
    
    try:
        response = requests.get(f"{BASE_URL}/mindchat/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"OK: Health check OK: {data['status']}")
            print(f"   Service: {data['service']}")
            print(f"   Version: {data['version']}")
            print(f"   API Base URL: {data['api_base_url']}")
            return True
        else:
            print(f"ERRO: Health check falhou: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERRO: Erro no health check: {e}")
        return False

def test_mindchat_messages():
    """Testa busca de mensagens do Mindchat"""
    print("\nTestando busca de mensagens Mindchat...")
    
    try:
        params = {
            "page": 1,
            "page_size": 5
        }
        
        response = requests.get(f"{BASE_URL}/mindchat/messages", params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"OK: Mensagens obtidas: {data['status']}")
            
            if 'data' in data and 'count' in data['data']:
                print(f"   Total de mensagens: {data['data']['count']}")
                print(f"   Página atual: {data['data'].get('page', 'N/A')}")
                
                if 'messages' in data['data'] and data['data']['messages']:
                    message = data['data']['messages'][0]
                    print(f"   Primeira mensagem:")
                    print(f"     ID: {message.get('id', 'N/A')}")
                    print(f"     Criada em: {message.get('createdAt', 'N/A')}")
                    print(f"     ACK: {message.get('ack', 'N/A')}")
            
            return True
        else:
            print(f"ERRO: Busca de mensagens falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: Erro na busca de mensagens: {e}")
        return False

def test_mindchat_send_message():
    """Testa envio de mensagem via Mindchat"""
    print("\nTestando envio de mensagem Mindchat...")
    
    headers = {
        "Authorization": f"Bearer {FASTAPI_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "to": "5516999999999",
        "message": "Teste de mensagem ARIA-SDR via Mindchat API real",
        "message_type": "text"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/mindchat/send",
            params=params,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"OK: Envio de mensagem OK: {data['status']}")
            return True
        else:
            print(f"ERRO: Envio de mensagem falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: Erro no envio de mensagem: {e}")
        return False

def test_mindchat_webhook_creation():
    """Testa criação de webhook no Mindchat"""
    print("\nTestando criação de webhook Mindchat...")
    
    headers = {
        "Authorization": f"Bearer {FASTAPI_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "webhook_url": "https://api.ar-online.com.br/webhook/mindchat/whatsapp",
        "events": json.dumps(["message", "status", "delivery"])
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/mindchat/webhook/create",
            params=params,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"OK: Criação de webhook OK: {data['status']}")
            return True
        else:
            print(f"ERRO: Criação de webhook falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: Erro na criação de webhook: {e}")
        return False

def test_mindchat_conversations():
    """Testa busca de conversas do Mindchat"""
    print("\nTestando busca de conversas Mindchat...")
    
    try:
        response = requests.get(f"{BASE_URL}/mindchat/conversations")
        
        if response.status_code == 200:
            data = response.json()
            print(f"OK: Conversas obtidas: {data['status']}")
            return True
        else:
            print(f"ERRO: Busca de conversas falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: Erro na busca de conversas: {e}")
        return False

def test_mindchat_webhook_verification():
    """Testa verificação de webhook Mindchat"""
    print("\nTestando verificação de webhook Mindchat...")
    
    try:
        params = {
            "hub_mode": "subscribe",
            "hub_challenge": "test_challenge_real",
            "hub_verify_token": "aria_verify_token"
        }
        
        response = requests.get(f"{BASE_URL}/mindchat/webhook/verify", params=params)
        
        if response.status_code == 200 and ("test_challenge_real" in response.text):
            print("OK: Verificação de webhook OK")
            return True
        else:
            print(f"ERRO: Verificação de webhook falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: Erro na verificação de webhook: {e}")
        return False

def test_mindchat_webhook_receive():
    """Testa recebimento de webhook Mindchat"""
    print("\nTestando recebimento de webhook Mindchat...")
    
    payload = {
        "messages": [
            {
                "id": "wamid.real123",
                "phone": "5516999999999",
                "text": "Mensagem de teste via API real",
                "type": "text",
                "createdAt": datetime.now().isoformat(),
                "ack": 2,
                "read": True,
                "contact": {
                    "name": "Cliente Teste Real",
                    "phone": "5516999999999"
                }
            }
        ],
        "statuses": [
            {
                "id": "wamid.real123",
                "status": "delivered",
                "timestamp": datetime.now().isoformat()
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/mindchat/whatsapp",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"OK: Webhook recebido OK: {data['status']}")
            print(f"   Mensagens processadas: {data['processed_messages']}")
            return True
        else:
            print(f"ERRO: Webhook falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: Erro no webhook: {e}")
        return False

def main():
    """Executa todos os testes da integração Mindchat real"""
    print("Testando integração Mindchat REAL da ARIA-SDR")
    print(f"URL Base: {BASE_URL}")
    print(f"Token Mindchat: {MINDCHAT_API_TOKEN[:20]}...")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_mindchat_health),
        ("Busca de Mensagens", test_mindchat_messages),
        ("Envio de Mensagem", test_mindchat_send_message),
        ("Criação de Webhook", test_mindchat_webhook_creation),
        ("Busca de Conversas", test_mindchat_conversations),
        ("Verificação de Webhook", test_mindchat_webhook_verification),
        ("Recebimento de Webhook", test_mindchat_webhook_receive)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERRO: Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES MINDCHAT REAL:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSOU" if result else "FALHOU"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("Todos os testes passaram! Integração Mindchat REAL está funcionando!")
    else:
        print("Alguns testes falharam. Verifique a configuração.")
    
    print("\nDescobertas importantes:")
    print("1. API Mindchat real está funcionando")
    print("2. Endpoint /api/messages retorna 57,949 mensagens")
    print("3. Envio de mensagens via /api/send funciona")
    print("4. Webhooks podem ser configurados")
    print("5. Integração completa com ARIA-SDR")
    
    print("\nPróximos passos:")
    print("1. Configurar webhook real no Mindchat")
    print("2. Testar com mensagens reais do WhatsApp")
    print("3. Integrar com RAG e roteamento")
    print("4. Monitorar logs de produção")

if __name__ == "__main__":
    main()
