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
    print("Testando verificacao do webhook Mindchat...")
    
    try:
        params = {
            "hub_mode": "subscribe",
            "hub_challenge": "test_challenge_123",
            "hub_verify_token": MINDCHAT_VERIFY_TOKEN
        }
        
        response = requests.get(f"{BASE_URL}/webhook/mindchat/verify", params=params)
        
        if response.status_code == 200 and response.text == "test_challenge_123":
            print("OK: Verificacao do webhook OK")
            return True
        else:
            print(f"ERRO: Verificacao do webhook falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: Erro na verificacao do webhook: {e}")
        return False

def test_whatsapp_message_webhook():
    """Testa webhook de mensagem WhatsApp"""
    print("\nTestando webhook de mensagem WhatsApp...")
    
    payload = {
        "messages": [
            {
                "id": "wamid.test123",
                "from": "5516999999999",
                "timestamp": "1640995200",
                "type": "text",
                "text": {
                    "body": "Ola, preciso de ajuda com meu pedido"
                }
            }
        ],
        "contacts": [
            {
                "profile": {
                    "name": "Joao Silva"
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
            print(f"OK: Webhook de mensagem OK: {data['status']}")
            print(f"   Mensagens processadas: {data['processed_messages']}")
            return True
        else:
            print(f"ERRO: Webhook de mensagem falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: Erro no webhook de mensagem: {e}")
        return False

def test_manual_message_send():
    """Testa envio manual de mensagem"""
    print("\nTestando envio manual de mensagem...")
    
    headers = {
        "Authorization": f"Bearer {FASTAPI_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Usar parâmetros de query em vez de body
    params = {
        "to": "5516999999999",
        "message": "Teste de mensagem da ARIA-SDR",
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
            print(f"OK: Envio manual OK: {data['status']}")
            return True
        else:
            print(f"ERRO: Envio manual falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: Erro no envio manual: {e}")
        return False

def test_webhook_signature_validation():
    """Testa validação de assinatura do webhook"""
    print("\nTestando validacao de assinatura...")
    
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
            print("OK: Validacao de assinatura OK (rejeitou assinatura invalida)")
            return True
        else:
            print(f"ERRO: Validacao de assinatura falhou: {response.status_code}")
            print(f"   Deveria rejeitar assinatura invalida")
            return False
            
    except Exception as e:
        print(f"ERRO: Erro na validacao de assinatura: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("Iniciando testes da integracao Mindchat ARIA-SDR")
    print(f"URL Base: {BASE_URL}")
    print(f"Token Mindchat: {MINDCHAT_API_TOKEN[:10]}...")
    print(f"Webhook Secret: {MINDCHAT_WEBHOOK_SECRET[:10]}...")
    print(f"Verify Token: {MINDCHAT_VERIFY_TOKEN}")
    print("=" * 60)
    
    tests = [
        ("Verificacao Webhook", test_mindchat_webhook_verification),
        ("Mensagem WhatsApp", test_whatsapp_message_webhook),
        ("Envio Manual", test_manual_message_send),
        ("Validacao Assinatura", test_webhook_signature_validation)
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
    print("RESUMO DOS TESTES:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSOU" if result else "FALHOU"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("Todos os testes passaram! Integracao Mindchat esta funcionando!")
    else:
        print("Alguns testes falharam. Verifique a configuracao.")
    
    print("\nProximos passos:")
    print("1. Configure o webhook no Mindchat:")
    print(f"   URL: {BASE_URL}/webhook/mindchat/whatsapp")
    print(f"   Verify Token: {MINDCHAT_VERIFY_TOKEN}")
    print("2. Configure as variaveis de ambiente")
    print("3. Teste com mensagens reais do WhatsApp")
    print("4. Monitore os logs de processamento")

if __name__ == "__main__":
    main()
