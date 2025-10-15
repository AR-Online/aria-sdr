#!/usr/bin/env python3
"""
Configurar Webhook Mindchat com ngrok
Execute: python configurar_webhook_ngrok.py
"""

import requests
import json
from datetime import datetime

# Configurações
MINDCHAT_TOKEN = "c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58"
API_BASE = "https://api-aronline.mindchatapp.com.br"
NGROK_URL = "https://e339776fe64f.ngrok-free.app"

def create_webhook():
    """Cria webhook no Mindchat com URL do ngrok"""
    print("CONFIGURANDO WEBHOOK MINDCHAT COM NGROK")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL ngrok: {NGROK_URL}")
    
    webhook_url = f"{NGROK_URL}/webhook/mindchat/whatsapp"
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {MINDCHAT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    webhook_data = {
        "url": webhook_url,
        "events": ["message", "status", "delivery"],
        "verify_token": "aria_verify_token",
        "active": True,
        "description": "ARIA-SDR Webhook via ngrok"
    }
    
    print(f"\nCriando webhook:")
    print(f"URL: {webhook_url}")
    print(f"Events: {webhook_data['events']}")
    print(f"Token: {webhook_data['verify_token']}")
    
    try:
        response = requests.post(f"{API_BASE}/webhook", json=webhook_data, headers=headers, timeout=10)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"\nWEBHOOK CRIADO COM SUCESSO!")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"\nERRO AO CRIAR WEBHOOK:")
            print(f"Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"\nERRO: {e}")
        return False

def test_webhook():
    """Testa o webhook criado"""
    print(f"\n{'='*60}")
    print(f"TESTANDO WEBHOOK")
    print(f"{'='*60}")
    
    webhook_url = f"{NGROK_URL}/webhook/mindchat/whatsapp"
    
    # Simular mensagem do WhatsApp
    test_payload = {
        "messages": [
            {
                "id": "test_msg_ngrok_123",
                "from": "5516999999999",
                "timestamp": str(int(datetime.now().timestamp())),
                "type": "text",
                "text": {
                    "body": "Teste de mensagem via ngrok - ARIA funcionando!"
                }
            }
        ],
        "contacts": [
            {
                "profile": {
                    "name": "Teste ngrok"
                }
            }
        ]
    }
    
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(webhook_url, json=test_payload, headers=headers, timeout=10)
        
        print(f"URL: {webhook_url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\nWEBHOOK FUNCIONANDO!")
            return True
        else:
            print("\nWEBHOOK COM PROBLEMAS!")
            return False
            
    except Exception as e:
        print(f"\nERRO: {e}")
        return False

def verify_webhook():
    """Verifica webhook de verificação"""
    print(f"\n{'='*60}")
    print(f"VERIFICANDO WEBHOOK DE VERIFICACAO")
    print(f"{'='*60}")
    
    verify_url = f"{NGROK_URL}/webhook/mindchat/verify"
    
    try:
        params = {
            "hub_mode": "subscribe",
            "hub_challenge": "test_ngrok_challenge",
            "hub_verify_token": "aria_verify_token"
        }
        
        response = requests.get(verify_url, params=params, timeout=10)
        
        print(f"URL: {verify_url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200 and "test_ngrok_challenge" in response.text:
            print("\nWEBHOOK DE VERIFICACAO FUNCIONANDO!")
            return True
        else:
            print("\nWEBHOOK DE VERIFICACAO COM PROBLEMAS!")
            return False
            
    except Exception as e:
        print(f"\nERRO: {e}")
        return False

def main():
    """Configuração completa do webhook"""
    print("CONFIGURACAO WEBHOOK MINDCHAT COM NGROK")
    print(f"URL ngrok: {NGROK_URL}")
    print(f"Webhook: {NGROK_URL}/webhook/mindchat/whatsapp")
    
    # Teste 1: Criar webhook
    webhook_ok = create_webhook()
    
    # Teste 2: Verificar webhook de verificação
    verify_ok = verify_webhook()
    
    # Teste 3: Testar webhook
    test_ok = test_webhook()
    
    # Resumo
    print(f"\n{'='*60}")
    print(f"RESUMO DA CONFIGURACAO")
    print(f"{'='*60}")
    print(f"[{'OK' if webhook_ok else 'ERRO'}] Webhook criado")
    print(f"[{'OK' if verify_ok else 'ERRO'}] Webhook de verificacao")
    print(f"[{'OK' if test_ok else 'ERRO'}] Webhook testado")
    
    if webhook_ok and verify_ok and test_ok:
        print(f"\nSUCESSO! ARIA FUNCIONANDO COM NGROK!")
        print(f"URL Publica: {NGROK_URL}")
        print(f"Webhook: {NGROK_URL}/webhook/mindchat/whatsapp")
        print(f"\nAGORA VOCE PODE TESTAR NO WHATSAPP!")
        print(f"Envie uma mensagem para (16) 99791-8658")
    else:
        print(f"\nPROBLEMAS NA CONFIGURACAO!")
        print(f"Verifique os logs acima para detalhes")

if __name__ == "__main__":
    main()
