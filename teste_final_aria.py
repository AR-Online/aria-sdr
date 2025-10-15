#!/usr/bin/env python3
"""
Teste Final - ARIA com ngrok
Execute: python teste_final_aria.py
"""

import requests
import json
from datetime import datetime

# Configurações
NGROK_URL = "https://e339776fe64f.ngrok-free.app"
MINDCHAT_TOKEN = "c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58"
API_BASE = "https://api-aronline.mindchatapp.com.br"

def test_aria_connection():
    """Testa conexão da ARIA"""
    print("TESTANDO CONEXAO DA ARIA")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {MINDCHAT_TOKEN}"
    }
    
    try:
        response = requests.get(f"{API_BASE}/api/connections", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            connections = data.get("connections", [])
            
            # Encontrar conexão ARIA
            aria_connection = None
            for conn in connections:
                if conn.get("name") == "ARIA":
                    aria_connection = conn
                    break
            
            if aria_connection:
                print(f"\nCONEXAO ARIA ENCONTRADA:")
                print(f"   ID: {aria_connection.get('id')}")
                print(f"   Nome: {aria_connection.get('name')}")
                print(f"   Status: {aria_connection.get('status')}")
                print(f"   Numero: {aria_connection.get('number')}")
                print(f"   Ultima atualizacao: {aria_connection.get('updatedAt')}")
                
                if aria_connection.get('status') == 'CONNECTED':
                    print(f"\nSTATUS: CONECTADA - ARIA funcionando!")
                    return True
                else:
                    print(f"\nSTATUS: DESCONECTADA - ARIA com problemas!")
                    return False
            else:
                print(f"\nCONEXAO ARIA NAO ENCONTRADA!")
                return False
        else:
            print(f"\nERRO AO BUSCAR CONEXOES:")
            print(f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\nERRO: {e}")
        return False

def test_ngrok_webhook():
    """Testa webhook via ngrok"""
    print(f"\n{'='*60}")
    print(f"TESTANDO WEBHOOK VIA NGROK")
    print(f"{'='*60}")
    
    webhook_url = f"{NGROK_URL}/webhook/mindchat/whatsapp"
    
    # Simular mensagem real do WhatsApp
    test_payload = {
        "messages": [
            {
                "id": f"test_aria_{int(datetime.now().timestamp())}",
                "from": "5516999999999",
                "timestamp": str(int(datetime.now().timestamp())),
                "type": "text",
                "text": {
                    "body": "Oi ARIA! Este é um teste via ngrok. Você está funcionando?"
                }
            }
        ],
        "contacts": [
            {
                "profile": {
                    "name": "Teste Final"
                }
            }
        ]
    }
    
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(webhook_url, json=test_payload, headers=headers, timeout=15)
        
        print(f"URL: {webhook_url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nWEBHOOK FUNCIONANDO!")
            print(f"Mensagens processadas: {data.get('processed_messages', 0)}")
            return True
        else:
            print(f"\nWEBHOOK COM PROBLEMAS!")
            return False
            
    except Exception as e:
        print(f"\nERRO: {e}")
        return False

def test_aria_health():
    """Testa health check da ARIA"""
    print(f"\n{'='*60}")
    print(f"TESTANDO HEALTH CHECK DA ARIA")
    print(f"{'='*60}")
    
    try:
        # Teste local
        response = requests.get("http://localhost:8000/mindchat/health", timeout=10)
        print(f"Health Check Local:")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Service: {data.get('service')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
        
        # Teste via ngrok
        ngrok_health_url = f"{NGROK_URL}/mindchat/health"
        response = requests.get(ngrok_health_url, timeout=10)
        print(f"\nHealth Check via ngrok:")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Service: {data.get('service')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"\nERRO: {e}")
        return False

def main():
    """Teste final completo"""
    print("TESTE FINAL - ARIA COM NGROK")
    print(f"URL ngrok: {NGROK_URL}")
    print(f"Webhook: {NGROK_URL}/webhook/mindchat/whatsapp")
    
    # Teste 1: Conexão ARIA
    connection_ok = test_aria_connection()
    
    # Teste 2: Health Check
    health_ok = test_aria_health()
    
    # Teste 3: Webhook via ngrok
    webhook_ok = test_ngrok_webhook()
    
    # Resumo final
    print(f"\n{'='*60}")
    print(f"RESUMO FINAL DO TESTE")
    print(f"{'='*60}")
    print(f"[{'OK' if connection_ok else 'ERRO'}] Conexao ARIA")
    print(f"[{'OK' if health_ok else 'ERRO'}] Health Check")
    print(f"[{'OK' if webhook_ok else 'ERRO'}] Webhook via ngrok")
    
    if connection_ok and health_ok and webhook_ok:
        print(f"\nSUCESSO TOTAL! ARIA FUNCIONANDO!")
        print(f"URL Publica: {NGROK_URL}")
        print(f"Webhook: {NGROK_URL}/webhook/mindchat/whatsapp")
        print(f"\nAGORA VOCE PODE TESTAR NO WHATSAPP!")
        print(f"Envie uma mensagem para (16) 99791-8658")
        print(f"A ARIA vai responder automaticamente!")
    else:
        print(f"\nPROBLEMAS DETECTADOS!")
        print(f"Verifique os logs acima para detalhes")

if __name__ == "__main__":
    main()
