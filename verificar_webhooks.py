#!/usr/bin/env python3
"""
Verificar Webhooks do Mindchat
Execute: python verificar_webhooks.py
"""

import requests
import json
from datetime import datetime

# Configurações
MINDCHAT_TOKEN = "c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58"
API_BASE = "https://api-aronline.mindchatapp.com.br"

def check_webhooks():
    """Verifica webhooks configurados"""
    print("VERIFICANDO WEBHOOKS DO MINDCHAT")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Base: {API_BASE}")
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {MINDCHAT_TOKEN}"
    }
    
    try:
        # Buscar webhooks
        response = requests.get(f"{API_BASE}/webhook", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nWEBHOOKS ENCONTRADOS:")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Se for uma lista de webhooks
            if isinstance(data, list):
                print(f"\nTotal de webhooks: {len(data)}")
                for i, webhook in enumerate(data, 1):
                    print(f"\nWebhook {i}:")
                    print(f"  ID: {webhook.get('id')}")
                    print(f"  URL: {webhook.get('url')}")
                    print(f"  Events: {webhook.get('events')}")
                    print(f"  Active: {webhook.get('active')}")
                    print(f"  Created: {webhook.get('createdAt')}")
            else:
                print(f"Dados do webhook: {data}")
            
            return True
        else:
            print(f"\nERRO AO BUSCAR WEBHOOKS:")
            print(f"Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"\nERRO: {e}")
        return False

def create_webhook():
    """Cria webhook para ARIA"""
    print(f"\n{'='*60}")
    print(f"CRIANDO WEBHOOK PARA ARIA")
    print(f"{'='*60}")
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {MINDCHAT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # URL do webhook (você precisa configurar uma URL pública)
    webhook_url = "https://api.ar-online.com.br/webhook/mindchat/whatsapp"
    
    webhook_data = {
        "url": webhook_url,
        "events": ["message", "status", "delivery"],
        "verify_token": "aria_verify_token",
        "active": True,
        "description": "ARIA-SDR Webhook Integration"
    }
    
    try:
        response = requests.post(f"{API_BASE}/webhook", json=webhook_data, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"WEBHOOK CRIADO COM SUCESSO!")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"ERRO AO CRIAR WEBHOOK:")
            print(f"Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_webhook_url():
    """Testa se a URL do webhook está acessível"""
    print(f"\n{'='*60}")
    print(f"TESTANDO URL DO WEBHOOK")
    print(f"{'='*60}")
    
    webhook_url = "https://api.ar-online.com.br/webhook/mindchat/whatsapp"
    
    try:
        # Teste simples
        response = requests.get(webhook_url, timeout=10)
        print(f"URL: {webhook_url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("URL ACESSIVEL!")
            return True
        else:
            print("URL NAO ACESSIVEL!")
            return False
            
    except Exception as e:
        print(f"ERRO AO TESTAR URL: {e}")
        return False

def main():
    """Executa verificação completa"""
    print("DIAGNOSTICO DE WEBHOOKS MINDCHAT")
    
    # Teste 1: Verificar webhooks existentes
    webhooks_ok = check_webhooks()
    
    # Teste 2: Testar URL do webhook
    url_ok = test_webhook_url()
    
    # Teste 3: Criar webhook se necessário
    if not webhooks_ok:
        print(f"\nTentando criar webhook...")
        create_webhook()
    
    # Resumo
    print(f"\n{'='*60}")
    print(f"RESUMO DO DIAGNOSTICO")
    print(f"{'='*60}")
    print(f"[{'OK' if webhooks_ok else 'ERRO'}] Webhooks: {'Encontrados' if webhooks_ok else 'Nao encontrados'}")
    print(f"[{'OK' if url_ok else 'ERRO'}] URL Webhook: {'Acessivel' if url_ok else 'Nao acessivel'}")
    
    if not url_ok:
        print(f"\nPROBLEMA IDENTIFICADO:")
        print(f"A URL do webhook nao esta acessivel publicamente!")
        print(f"Voce precisa:")
        print(f"1. Configurar um servidor publico")
        print(f"2. Ou usar ngrok para tunelamento")
        print(f"3. Ou configurar um webhook diferente")

if __name__ == "__main__":
    main()
