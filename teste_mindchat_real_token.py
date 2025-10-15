#!/usr/bin/env python3
"""
Teste com Token Real do Mindchat
Execute: python teste_mindchat_real_token.py
"""

import requests
import json
import os
from datetime import datetime

# Configurações reais do Mindchat
MINDCHAT_API_TOKEN = "c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58"
MINDCHAT_API_BASE_URL = "https://api-aronline.mindchatapp.com.br"
BASE_URL = "http://localhost:8000"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"TESTE REAL: {title}")
    print(f"{'='*60}")

def print_result(test_name, success, details=""):
    status = "PASSOU" if success else "FALHOU"
    print(f"[{status}] {test_name}")
    if details:
        print(f"   {details}")

def test_mindchat_api_direct():
    """Teste direto na API do Mindchat"""
    print_header("TESTE DIRETO NA API MINDCHAT")
    
    try:
        headers = {
            "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Teste 1: Health check direto
        print("Testando health check direto...")
        response = requests.get(f"{MINDCHAT_API_BASE_URL}/health", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        # Teste 2: Buscar mensagens direto
        print("\nTestando busca de mensagens direto...")
        response = requests.get(f"{MINDCHAT_API_BASE_URL}/api/messages?page=1&pageSize=5", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total de mensagens: {data.get('count', 'N/A')}")
        else:
            print(f"   Response: {response.text[:200]}...")
        
        # Teste 3: Buscar conversas direto
        print("\nTestando busca de conversas direto...")
        response = requests.get(f"{MINDCHAT_API_BASE_URL}/api/conversations", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total de conversas: {len(data.get('conversations', []))}")
        else:
            print(f"   Response: {response.text[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_aria_endpoints_with_real_token():
    """Teste dos endpoints da ARIA com token real"""
    print_header("TESTE ENDPOINTS ARIA COM TOKEN REAL")
    
    # Configurar variáveis de ambiente temporariamente
    os.environ["MINDCHAT_API_TOKEN"] = MINDCHAT_API_TOKEN
    os.environ["MINDCHAT_API_BASE_URL"] = MINDCHAT_API_BASE_URL
    
    tests = [
        ("Health Check ARIA", f"{BASE_URL}/mindchat/health"),
        ("Buscar Mensagens ARIA", f"{BASE_URL}/mindchat/messages?page=1&page_size=5"),
        ("Buscar Conversas ARIA", f"{BASE_URL}/mindchat/conversations"),
        ("Verificação Webhook ARIA", f"{BASE_URL}/mindchat/webhook/verify?hub_mode=subscribe&hub_challenge=teste_real&hub_verify_token=aria_verify_token")
    ]
    
    results = []
    
    for test_name, url in tests:
        try:
            print(f"\nTestando: {test_name}")
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:300]}...")
                    results.append((test_name, True))
                except:
                    print(f"   Response: {response.text[:200]}...")
                    results.append((test_name, True))
            else:
                print(f"   Response: {response.text[:200]}...")
                results.append((test_name, False))
                
        except Exception as e:
            print(f"   ERRO: {e}")
            results.append((test_name, False))
    
    return results

def test_send_message_real():
    """Teste de envio de mensagem real"""
    print_header("TESTE ENVIO DE MENSAGEM REAL")
    
    try:
        # Teste via ARIA
        params = {
            "to": "5516999999999",  # Número de teste
            "message": f"Teste real ARIA-SDR - {datetime.now().strftime('%H:%M:%S')}",
            "message_type": "text"
        }
        
        print("Enviando via endpoint ARIA...")
        response = requests.post(f"{BASE_URL}/mindchat/send", params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print_result("Envio via ARIA", True, "Mensagem enviada com sucesso")
            return True
        else:
            print_result("Envio via ARIA", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Envio via ARIA", False, f"Erro: {e}")
        return False

def main():
    """Executa todos os testes com token real"""
    print("TESTE COMPLETO COM TOKEN REAL DO MINDCHAT")
    print(f"Token: {MINDCHAT_API_TOKEN[:20]}...")
    print(f"URL Base: {MINDCHAT_API_BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Teste 1: API direta do Mindchat
    print_header("TESTE 1: API DIRETA MINDCHAT")
    api_direct_ok = test_mindchat_api_direct()
    
    # Teste 2: Endpoints ARIA
    print_header("TESTE 2: ENDPOINTS ARIA")
    aria_results = test_aria_endpoints_with_real_token()
    
    # Teste 3: Envio de mensagem
    print_header("TESTE 3: ENVIO DE MENSAGEM")
    send_ok = test_send_message_real()
    
    # Resumo final
    print_header("RESUMO DOS TESTES")
    
    print(f"[{'PASSOU' if api_direct_ok else 'FALHOU'}] API Direta Mindchat")
    
    for test_name, result in aria_results:
        print(f"[{'PASSOU' if result else 'FALHOU'}] {test_name}")
    
    print(f"[{'PASSOU' if send_ok else 'FALHOU'}] Envio de Mensagem")
    
    total_tests = 1 + len(aria_results) + 1
    passed_tests = (1 if api_direct_ok else 0) + sum(1 for _, result in aria_results if result) + (1 if send_ok else 0)
    
    print(f"\nRESULTADO FINAL: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("TODOS OS TESTES PASSARAM! Token real funcionando!")
    elif passed_tests >= total_tests * 0.8:
        print("Maioria dos testes passou. Token real funcionando parcialmente.")
    else:
        print("Muitos testes falharam. Verifique a configuracao do token.")
    
    print(f"\nToken usado: {MINDCHAT_API_TOKEN[:20]}...")
    print(f"URL Base: {MINDCHAT_API_BASE_URL}")

if __name__ == "__main__":
    main()
