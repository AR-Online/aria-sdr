#!/usr/bin/env python3
"""
Script para explorar a API do Mindchat e descobrir webhooks
Baseado na documentação: https://api-aronline.mindchatapp.com.br/api-docs/
"""

import requests
import json
import os
from typing import Dict, Any, List

# Configurações
MINDCHAT_API_TOKEN = "c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58"
MINDCHAT_API_BASE_URL = "https://api-aronline.mindchatapp.com.br"
MINDCHAT_API_DOCS = "https://api-aronline.mindchatapp.com.br/api-docs/"

def test_mindchat_api_connection():
    """Testa conexão com a API do Mindchat"""
    print("Testando conexao com API do Mindchat...")
    
    headers = {
        "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Testar endpoint básico
        response = requests.get(f"{MINDCHAT_API_BASE_URL}/", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("OK: Conexao com API Mindchat estabelecida")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return True
        else:
            print(f"ERRO: Conexao falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: Erro na conexao: {e}")
        return False

def explore_mindchat_endpoints():
    """Explora endpoints disponíveis na API do Mindchat"""
    print("\nExplorando endpoints da API Mindchat...")
    
    headers = {
        "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Endpoints comuns para explorar
    endpoints_to_test = [
        "/api/v1/",
        "/api/",
        "/webhooks",
        "/webhook",
        "/messages",
        "/conversations",
        "/contacts",
        "/templates",
        "/status",
        "/health",
        "/docs",
        "/swagger",
        "/openapi.json"
    ]
    
    available_endpoints = []
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{MINDCHAT_API_BASE_URL}{endpoint}"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code in [200, 201, 202]:
                print(f"OK: {endpoint} - Status: {response.status_code}")
                available_endpoints.append(endpoint)
                
                # Se for JSON, mostrar estrutura
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        keys = list(data.keys())[:5]  # Primeiras 5 chaves
                        print(f"   Keys: {keys}")
                except:
                    pass
                    
            elif response.status_code == 404:
                print(f"INFO: {endpoint} - Nao encontrado (404)")
            elif response.status_code == 401:
                print(f"ERRO: {endpoint} - Nao autorizado (401)")
            else:
                print(f"INFO: {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"ERRO: {endpoint} - {e}")
    
    return available_endpoints

def test_mindchat_webhooks():
    """Testa funcionalidades de webhook do Mindchat"""
    print("\nTestando webhooks do Mindchat...")
    
    headers = {
        "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Testar endpoints de webhook
    webhook_endpoints = [
        "/webhooks",
        "/webhook",
        "/api/v1/webhooks",
        "/api/webhooks"
    ]
    
    webhook_info = {}
    
    for endpoint in webhook_endpoints:
        try:
            url = f"{MINDCHAT_API_BASE_URL}{endpoint}"
            
            # GET - Listar webhooks
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"OK: {endpoint} - Webhooks disponiveis")
                try:
                    data = response.json()
                    webhook_info[endpoint] = data
                    print(f"   Data: {json.dumps(data, indent=2)[:300]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"INFO: {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"ERRO: {endpoint} - {e}")
    
    return webhook_info

def test_mindchat_messages():
    """Testa funcionalidades de mensagem do Mindchat"""
    print("\nTestando funcionalidades de mensagem...")
    
    headers = {
        "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Testar endpoints de mensagem
    message_endpoints = [
        "/messages",
        "/api/v1/messages",
        "/api/messages",
        "/send",
        "/api/v1/send"
    ]
    
    for endpoint in message_endpoints:
        try:
            url = f"{MINDCHAT_API_BASE_URL}{endpoint}"
            
            # GET - Informações sobre mensagens
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"OK: {endpoint} - Endpoint de mensagem disponivel")
                try:
                    data = response.json()
                    print(f"   Data: {json.dumps(data, indent=2)[:300]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"INFO: {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"ERRO: {endpoint} - {e}")

def test_mindchat_templates():
    """Testa templates de mensagem do Mindchat"""
    print("\nTestando templates de mensagem...")
    
    headers = {
        "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Testar endpoints de template
    template_endpoints = [
        "/templates",
        "/api/v1/templates",
        "/api/templates",
        "/message-templates"
    ]
    
    for endpoint in template_endpoints:
        try:
            url = f"{MINDCHAT_API_BASE_URL}{endpoint}"
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"OK: {endpoint} - Templates disponiveis")
                try:
                    data = response.json()
                    print(f"   Data: {json.dumps(data, indent=2)[:300]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"INFO: {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"ERRO: {endpoint} - {e}")

def test_mindchat_conversations():
    """Testa funcionalidades de conversa"""
    print("\nTestando funcionalidades de conversa...")
    
    headers = {
        "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Testar endpoints de conversa
    conversation_endpoints = [
        "/conversations",
        "/api/v1/conversations",
        "/api/conversations",
        "/chats",
        "/api/v1/chats"
    ]
    
    for endpoint in conversation_endpoints:
        try:
            url = f"{MINDCHAT_API_BASE_URL}{endpoint}"
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"OK: {endpoint} - Conversas disponiveis")
                try:
                    data = response.json()
                    print(f"   Data: {json.dumps(data, indent=2)[:300]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"INFO: {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"ERRO: {endpoint} - {e}")

def create_mindchat_webhook():
    """Tenta criar um webhook no Mindchat"""
    print("\nTentando criar webhook no Mindchat...")
    
    headers = {
        "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    webhook_payload = {
        "url": "https://api.ar-online.com.br/webhook/mindchat/whatsapp",
        "events": ["message", "status", "delivery"],
        "verify_token": "aria_verify_token",
        "active": True
    }
    
    webhook_endpoints = [
        "/webhooks",
        "/webhook",
        "/api/v1/webhooks",
        "/api/webhooks"
    ]
    
    for endpoint in webhook_endpoints:
        try:
            url = f"{MINDCHAT_API_BASE_URL}{endpoint}"
            
            response = requests.post(url, json=webhook_payload, headers=headers, timeout=10)
            
            if response.status_code in [200, 201, 202]:
                print(f"OK: {endpoint} - Webhook criado com sucesso")
                try:
                    data = response.json()
                    print(f"   Webhook ID: {data.get('id', 'N/A')}")
                    print(f"   Data: {json.dumps(data, indent=2)[:300]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
                return True
            else:
                print(f"INFO: {endpoint} - Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"ERRO: {endpoint} - {e}")
    
    return False

def main():
    """Executa exploração completa da API Mindchat"""
    print("Explorando API do Mindchat")
    print(f"API Base URL: {MINDCHAT_API_BASE_URL}")
    print(f"API Docs: {MINDCHAT_API_DOCS}")
    print(f"Token: {MINDCHAT_API_TOKEN[:20]}...")
    print("=" * 60)
    
    # Executar testes
    tests = [
        ("Conexao API", test_mindchat_api_connection),
        ("Endpoints Disponiveis", explore_mindchat_endpoints),
        ("Webhooks", test_mindchat_webhooks),
        ("Mensagens", test_mindchat_messages),
        ("Templates", test_mindchat_templates),
        ("Conversas", test_mindchat_conversations),
        ("Criar Webhook", create_mindchat_webhook)
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
    print("RESUMO DA EXPLORACAO:")
    
    for test_name, result in results:
        status = "SUCESSO" if result else "FALHOU"
        print(f"   {test_name}: {status}")
    
    print("\nProximos passos:")
    print("1. Analisar endpoints descobertos")
    print("2. Configurar webhooks se disponiveis")
    print("3. Testar envio de mensagens")
    print("4. Integrar com ARIA-SDR")

if __name__ == "__main__":
    main()
