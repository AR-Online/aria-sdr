#!/usr/bin/env python3
"""
Script de teste para integração Mindchat da ARIA-SDR
Testa os endpoints de webhook e envio de mensagens
"""

import json
import requests
import os
import hmac
import hashlib
from datetime import datetime
from typing import Dict, Any

# Configurações
BASE_URL = "http://localhost:8000"  # URL da API ARIA
MINDCHAT_API_TOKEN = os.getenv("MINDCHAT_API_TOKEN", "test_token")
MINDCHAT_WEBHOOK_SECRET = os.getenv("MINDCHAT_WEBHOOK_SECRET", "test_secret")
MINDCHAT_VERIFY_TOKEN = os.getenv("MINDCHAT_VERIFY_TOKEN", "aria_verify_token")
FASTAPI_BEARER_TOKEN = os.getenv("FASTAPI_BEARER_TOKEN", "dtransforma2026")

def generate_webhook_signature(payload: str, secret: str) -> str:
    """Gera assinatura HMAC para webhook"""
    signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

def test_mindchat_webhook_verification():
    """Testa verificação do webhook Mindchat"""
    print("🔍 Testando verificação do webhook Mindchat...")
    
    try:
        params = {
            "hub.mode": "subscribe",
            "hub.challenge": "test_challenge_123",
            "hub.verify_token": MINDCHAT_VERIFY_TOKEN
        }
        
        response = requests.get(f"{BASE_URL}/webhook/mindchat/verify", params=params)
        
        if response.status_code == 200 and response.text == "test_challenge_123":
            print("✅ Verificação do webhook OK")
            return True
        else:
            print(f"❌ Verificação do webhook falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação do webhook: {e}")
        return False

def test_whatsapp_message_webhook():
    """Testa webhook de mensagem WhatsApp"""
    print("\n🔍 Testando webhook de mensagem WhatsApp...")
    
    payload = {
        "messages": [
            {
                "id": "wamid.test123",
                "from": "5516999999999",
                "timestamp": "1640995200",
                "type": "text",
                "text": {
                    "body": "Olá, preciso de ajuda com meu pedido"
                }
            }
        ],
        "contacts": [
            {
                "profile": {
                    "name": "João Silva"
                },
                "wa_id": "5516999999999"
            }
        ]
    }
    
    payload_str = json.dumps(payload)
    signature = generate_webhook_signature(payload_str, MINDCHAT_WEBHOOK_SECRET)
    
    headers = {
        "Content-Type": "application/json",
        "X-Mindchat-Signature": signature,
        "X-Mindchat-Timestamp": "1640995200"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/mindchat/whatsapp",
            data=payload_str,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Webhook de mensagem OK: {data['status']}")
            print(f"   Mensagens processadas: {data['processed_messages']}")
            return True
        else:
            print(f"❌ Webhook de mensagem falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no webhook de mensagem: {e}")
        return False

def test_interactive_message_webhook():
    """Testa webhook de mensagem interativa"""
    print("\n🔍 Testando webhook de mensagem interativa...")
    
    payload = {
        "messages": [
            {
                "id": "wamid.test456",
                "from": "5516999999999",
                "timestamp": "1640995200",
                "type": "interactive",
                "interactive": {
                    "type": "button_reply",
                    "button_reply": {
                        "id": "btn_faq",
                        "title": "FAQ"
                    }
                }
            }
        ],
        "contacts": [
            {
                "profile": {
                    "name": "Maria Santos"
                },
                "wa_id": "5516999999999"
            }
        ]
    }
    
    payload_str = json.dumps(payload)
    signature = generate_webhook_signature(payload_str, MINDCHAT_WEBHOOK_SECRET)
    
    headers = {
        "Content-Type": "application/json",
        "X-Mindchat-Signature": signature,
        "X-Mindchat-Timestamp": "1640995200"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/mindchat/whatsapp",
            data=payload_str,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Webhook interativo OK: {data['status']}")
            print(f"   Mensagens processadas: {data['processed_messages']}")
            return True
        else:
            print(f"❌ Webhook interativo falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no webhook interativo: {e}")
        return False

def test_status_webhook():
    """Testa webhook de status"""
    print("\n🔍 Testando webhook de status...")
    
    payload = {
        "statuses": [
            {
                "id": "wamid.test123",
                "status": "delivered",
                "timestamp": "1640995200",
                "recipient_id": "5516999999999"
            }
        ]
    }
    
    payload_str = json.dumps(payload)
    signature = generate_webhook_signature(payload_str, MINDCHAT_WEBHOOK_SECRET)
    
    headers = {
        "Content-Type": "application/json",
        "X-Mindchat-Signature": signature,
        "X-Mindchat-Timestamp": "1640995200"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/mindchat/status",
            data=payload_str,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Webhook de status OK: {data['status']}")
            return True
        else:
            print(f"❌ Webhook de status falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no webhook de status: {e}")
        return False

def test_manual_message_send():
    """Testa envio manual de mensagem"""
    print("\n🔍 Testando envio manual de mensagem...")
    
    headers = {
        "Authorization": f"Bearer {FASTAPI_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "to": "5516999999999",
        "message": "🤖 Teste de mensagem da ARIA-SDR",
        "message_type": "text"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/mindchat/send",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Envio manual OK: {data['status']}")
            return True
        else:
            print(f"❌ Envio manual falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no envio manual: {e}")
        return False

def test_webhook_signature_validation():
    """Testa validação de assinatura do webhook"""
    print("\n🔍 Testando validação de assinatura...")
    
    payload = {
        "messages": [
            {
                "id": "wamid.test789",
                "from": "5516999999999",
                "timestamp": "1640995200",
                "type": "text",
                "text": {
                    "body": "Mensagem de teste"
                }
            }
        ],
        "contacts": [
            {
                "profile": {
                    "name": "Teste User"
                },
                "wa_id": "5516999999999"
            }
        ]
    }
    
    payload_str = json.dumps(payload)
    
    # Teste com assinatura inválida
    headers_invalid = {
        "Content-Type": "application/json",
        "X-Mindchat-Signature": "sha256=invalid_signature",
        "X-Mindchat-Timestamp": "1640995200"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/mindchat/whatsapp",
            data=payload_str,
            headers=headers_invalid
        )
        
        if response.status_code == 401:
            print("✅ Validação de assinatura OK (rejeitou assinatura inválida)")
            return True
        else:
            print(f"❌ Validação de assinatura falhou: {response.status_code}")
            print(f"   Deveria rejeitar assinatura inválida")
            return False
            
    except Exception as e:
        print(f"❌ Erro na validação de assinatura: {e}")
        return False

def test_routing_integration():
    """Testa integração com roteamento"""
    print("\n🔍 Testando integração com roteamento...")
    
    # Teste de mensagem que deve ir para FAQ
    payload_faq = {
        "messages": [
            {
                "id": "wamid.faq123",
                "from": "5516999999999",
                "timestamp": "1640995200",
                "type": "text",
                "text": {
                    "body": "Qual é o horário de funcionamento?"
                }
            }
        ],
        "contacts": [
            {
                "profile": {
                    "name": "Cliente FAQ"
                },
                "wa_id": "5516999999999"
            }
        ]
    }
    
    payload_str = json.dumps(payload_faq)
    signature = generate_webhook_signature(payload_str, MINDCHAT_WEBHOOK_SECRET)
    
    headers = {
        "Content-Type": "application/json",
        "X-Mindchat-Signature": signature,
        "X-Mindchat-Timestamp": "1640995200"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/mindchat/whatsapp",
            data=payload_str,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Integração de roteamento OK: {data['status']}")
            
            # Verificar se a resposta contém informações de roteamento
            if data.get('responses'):
                routing_action = data['responses'][0].get('routing_action', 'unknown')
                confidence = data['responses'][0].get('confidence', 0.0)
                print(f"   Ação de roteamento: {routing_action}")
                print(f"   Confiança: {confidence:.2f}")
            
            return True
        else:
            print(f"❌ Integração de roteamento falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na integração de roteamento: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes da integração Mindchat ARIA-SDR")
    print(f"📡 URL Base: {BASE_URL}")
    print(f"🔑 Token Mindchat: {MINDCHAT_API_TOKEN[:10]}...")
    print(f"🔐 Webhook Secret: {MINDCHAT_WEBHOOK_SECRET[:10]}...")
    print(f"✅ Verify Token: {MINDCHAT_VERIFY_TOKEN}")
    print("=" * 60)
    
    tests = [
        ("Verificação Webhook", test_mindchat_webhook_verification),
        ("Mensagem WhatsApp", test_whatsapp_message_webhook),
        ("Mensagem Interativa", test_interactive_message_webhook),
        ("Webhook de Status", test_status_webhook),
        ("Envio Manual", test_manual_message_send),
        ("Validação Assinatura", test_webhook_signature_validation),
        ("Integração Roteamento", test_routing_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Integração Mindchat está funcionando!")
    else:
        print("⚠️  Alguns testes falharam. Verifique a configuração.")
    
    print("\n📋 Próximos passos:")
    print("1. Configure o webhook no Mindchat:")
    print(f"   URL: {BASE_URL}/webhook/mindchat/whatsapp")
    print(f"   Verify Token: {MINDCHAT_VERIFY_TOKEN}")
    print("2. Configure as variáveis de ambiente")
    print("3. Teste com mensagens reais do WhatsApp")
    print("4. Monitore os logs de processamento")

if __name__ == "__main__":
    main()
