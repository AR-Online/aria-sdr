#!/usr/bin/env python3
"""
Script de Teste Simples - Integração Mindchat ARIA-SDR
Execute: python teste_simples.py
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
FASTAPI_BEARER_TOKEN = "test-token"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"TESTE: {title}")
    print(f"{'='*60}")

def print_result(test_name, success, details=""):
    status = "PASSOU" if success else "FALHOU"
    print(f"[{status}] {test_name}")
    if details:
        print(f"   {details}")

def test_health():
    """Teste 1: Health Check"""
    print_header("TESTE 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/mindchat/health")
        if response.status_code == 200:
            data = response.json()
            print_result("Health Check", True, f"Status: {data['status']}")
            return True
        else:
            print_result("Health Check", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Health Check", False, f"Erro: {e}")
        return False

def test_webhook_verify():
    """Teste 2: Verificação de Webhook"""
    print_header("TESTE 2: Verificação de Webhook")
    
    try:
        params = {
            "hub_mode": "subscribe",
            "hub_challenge": "teste_manual_123",
            "hub_verify_token": "aria_verify_token"
        }
        
        response = requests.get(f"{BASE_URL}/mindchat/webhook/verify", params=params)
        
        if response.status_code == 200 and "teste_manual_123" in response.text:
            print_result("Verificação de Webhook", True, "Token verificado com sucesso")
            return True
        else:
            print_result("Verificação de Webhook", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Verificação de Webhook", False, f"Erro: {e}")
        return False

def test_send_message():
    """Teste 3: Envio de Mensagem"""
    print_header("TESTE 3: Envio de Mensagem")
    
    try:
        params = {
            "to": "5516999999999",
            "message": f"Teste manual ARIA-SDR - {datetime.now().strftime('%H:%M:%S')}",
            "message_type": "text"
        }
        
        response = requests.post(f"{BASE_URL}/mindchat/send", params=params)
        
        if response.status_code == 200:
            data = response.json()
            print_result("Envio de Mensagem", True, f"Status: {data.get('status', 'OK')}")
            return True
        else:
            print_result("Envio de Mensagem", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Envio de Mensagem", False, f"Erro: {e}")
        return False

def test_webhook_receive():
    """Teste 4: Recebimento de Webhook"""
    print_header("TESTE 4: Recebimento de Webhook")
    
    try:
        payload = {
            "messages": [
                {
                    "id": "msg_teste_manual",
                    "from": "5516999999999",
                    "timestamp": str(int(datetime.now().timestamp())),
                    "type": "text",
                    "text": {
                        "body": "Olá ARIA! Este é um teste manual."
                    }
                }
            ],
            "contacts": [
                {
                    "profile": {
                        "name": "Teste Manual"
                    }
                }
            ]
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/webhook/mindchat/whatsapp",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result("Recebimento de Webhook", True, f"Mensagens processadas: {data.get('processed_messages', 0)}")
            return True
        else:
            print_result("Recebimento de Webhook", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Recebimento de Webhook", False, f"Erro: {e}")
        return False

def test_messages_list():
    """Teste 5: Lista de Mensagens"""
    print_header("TESTE 5: Lista de Mensagens")
    
    try:
        response = requests.get(f"{BASE_URL}/mindchat/messages?page=1&page_size=3")
        
        if response.status_code == 200:
            data = response.json()
            print_result("Lista de Mensagens", True, f"Status: {data.get('status', 'OK')}")
            return True
        else:
            print_result("Lista de Mensagens", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Lista de Mensagens", False, f"Erro: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("INICIANDO TESTES MANUAIS - INTEGRACAO MINDCHAT ARIA-SDR")
    print(f"URL Base: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Health Check", test_health),
        ("Verificação de Webhook", test_webhook_verify),
        ("Envio de Mensagem", test_send_message),
        ("Recebimento de Webhook", test_webhook_receive),
        ("Lista de Mensagens", test_messages_list)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERRO CRÍTICO no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo final
    print_header("RESUMO DOS TESTES")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSOU" if result else "FALHOU"
        print(f"   [{status}] {test_name}")
        if result:
            passed += 1
    
    print(f"\nRESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("TODOS OS TESTES PASSARAM! Integracao funcionando perfeitamente!")
    elif passed >= total * 0.8:
        print("Maioria dos testes passou. Verifique os que falharam.")
    else:
        print("Muitos testes falharam. Verifique a configuracao.")
    
    print(f"\nPara mais detalhes, consulte: GUIA_TESTE_MINDCHAT.md")

if __name__ == "__main__":
    main()
