#!/usr/bin/env python3
"""
Teste de Conexões Mindchat
Execute: python teste_conexoes_mindchat.py
"""

import requests
import json
from datetime import datetime

# Tokens para teste
TOKENS = {
    "dtranforma2026": "dtranforma2026",
    "mindchat_real": "c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58"
}

API_BASE = "https://api-aronline.mindchatapp.com.br"

def test_connections(token_name, token):
    """Testa API de conexões"""
    print(f"\n{'='*60}")
    print(f"TESTE: {token_name}")
    print(f"{'='*60}")
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        # Teste 1: Health check
        print("1. Testando health check...")
        response = requests.get(f"{API_BASE}/health", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
        else:
            print(f"   Error: {response.text}")
        
        # Teste 2: Conexões
        print("\n2. Testando API de conexões...")
        response = requests.get(f"{API_BASE}/api/connections", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            # Verificar se há conexões ativas
            if isinstance(data, list):
                print(f"   Total de conexões: {len(data)}")
                for i, conn in enumerate(data):
                    print(f"   Conexão {i+1}: {conn}")
            elif isinstance(data, dict):
                print(f"   Dados da conexão: {data}")
        else:
            print(f"   Error: {response.text}")
        
        # Teste 3: Mensagens
        print("\n3. Testando API de mensagens...")
        response = requests.get(f"{API_BASE}/api/messages?page=1&pageSize=3", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total de mensagens: {data.get('count', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
            
        return True
        
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("TESTE DE CONEXOES MINDCHAT")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Base: {API_BASE}")
    
    results = []
    
    for token_name, token in TOKENS.items():
        result = test_connections(token_name, token)
        results.append((token_name, result))
    
    # Resumo
    print(f"\n{'='*60}")
    print("RESUMO DOS TESTES")
    print(f"{'='*60}")
    
    for token_name, result in results:
        status = "PASSOU" if result else "FALHOU"
        print(f"[{status}] {token_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nRESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("TODOS OS TESTES PASSARAM!")
    elif passed > 0:
        print("ALGUNS TESTES PASSARAM!")
    else:
        print("NENHUM TESTE PASSOU!")

if __name__ == "__main__":
    main()
