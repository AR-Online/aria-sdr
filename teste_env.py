#!/usr/bin/env python3
"""
Teste de Variáveis de Ambiente
Execute: python teste_env.py
"""

import os
from dotenv import load_dotenv

# Carregar arquivo .env
load_dotenv()

print("=== TESTE DE VARIAVEIS DE AMBIENTE ===")
print(f"MINDCHAT_API_TOKEN: {os.getenv('MINDCHAT_API_TOKEN', 'NAO_ENCONTRADO')[:20]}...")
print(f"MINDCHAT_API_BASE_URL: {os.getenv('MINDCHAT_API_BASE_URL', 'NAO_ENCONTRADO')}")
print(f"MINDCHAT_API_DOCS: {os.getenv('MINDCHAT_API_DOCS', 'NAO_ENCONTRADO')}")
print(f"MINDCHAT_WEBHOOK_SECRET: {os.getenv('MINDCHAT_WEBHOOK_SECRET', 'NAO_ENCONTRADO')}")
print(f"MINDCHAT_VERIFY_TOKEN: {os.getenv('MINDCHAT_VERIFY_TOKEN', 'NAO_ENCONTRADO')}")

print("\n=== TESTE DE CONEXAO DIRETA ===")
import requests

token = os.getenv('MINDCHAT_API_TOKEN')
base_url = os.getenv('MINDCHAT_API_BASE_URL')

if token and base_url:
    print(f"Token: {token[:20]}...")
    print(f"Base URL: {base_url}")
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Teste health check
        response = requests.get(f"{base_url}/health", headers=headers, timeout=10)
        print(f"Health Check Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health Check Response: {response.json()}")
        
        # Teste mensagens
        response = requests.get(f"{base_url}/api/messages?page=1&pageSize=3", headers=headers, timeout=10)
        print(f"Messages Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total Messages: {data.get('count', 'N/A')}")
        else:
            print(f"Messages Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"ERRO: {e}")
else:
    print("ERRO: Token ou Base URL nao encontrados!")
