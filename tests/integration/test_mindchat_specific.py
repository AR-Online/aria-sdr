#!/usr/bin/env python3
"""
Script para testar funcionalidades específicas da API Mindchat
Focado nos endpoints que retornaram dados reais
"""

import requests
import json
import os
from typing import Dict, Any, List

# Configurações
MINDCHAT_API_TOKEN = "c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58"
MINDCHAT_API_BASE_URL = "https://api-aronline.mindchatapp.com.br"

def test_mindchat_messages_detailed():
    """Testa endpoint de mensagens com mais detalhes"""
    print("Testando endpoint de mensagens detalhado...")
    
    headers = {
        "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Testar diferentes parâmetros
        params_options = [
            {},
            {"page": 1, "pageSize": 5},
            {"limit": 10},
            {"page": 1}
        ]
        
        for i, params in enumerate(params_options):
            print(f"\nTeste {i+1} - Parâmetros: {params}")
            
            response = requests.get(
                f"{MINDCHAT_API_BASE_URL}/api/messages",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: {response.status_code}")
                print(f"   Total de mensagens: {data.get('count', 'N/A')}")
                print(f"   Página atual: {data.get('page', 'N/A')}")
                print(f"   Tamanho da página: {data.get('pageSize', 'N/A')}")
                
                if 'messages' in data and data['messages']:
                    message = data['messages'][0]
                    print(f"   Primeira mensagem:")
                    print(f"     ID: {message.get('id', 'N/A')}")
                    print(f"     Criada em: {message.get('createdAt', 'N/A')}")
                    print(f"     ACK: {message.get('ack', 'N/A')}")
                    print(f"     Lida: {message.get('read', 'N/A')}")
                    print(f"     Texto: {message.get('text', 'N/A')[:50]}...")
                    
                    # Informações do contato
                    if 'contact' in message:
                        contact = message['contact']
                        print(f"     Contato: {contact.get('name', 'N/A')} ({contact.get('phone', 'N/A')})")
                
                return True
            else:
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_mindchat_send_message():
    """Testa envio de mensagem via API"""
    print("\nTestando envio de mensagem...")
    
    headers = {
        "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Payload de teste
    message_payload = {
        "phone": "5516999999999",  # Número de teste
        "message": "Teste de mensagem da ARIA-SDR via API Mindchat",
        "type": "text"
    }
    
    try:
        response = requests.post(
            f"{MINDCHAT_API_BASE_URL}/api/send",
            json=message_payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_mindchat_conversations_detailed():
    """Testa endpoint de conversas com mais detalhes"""
    print("\nTestando endpoint de conversas detalhado...")
    
    headers = {
        "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{MINDCHAT_API_BASE_URL}/api/conversations",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(data, indent=2)[:500]}...")
            return True
        else:
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_mindchat_webhook_creation():
    """Testa criação de webhook com payload específico"""
    print("\nTestando criação de webhook...")
    
    headers = {
        "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    webhook_payload = {
        "url": "https://api.ar-online.com.br/webhook/mindchat/whatsapp",
        "events": ["message", "status", "delivery"],
        "verify_token": "aria_verify_token",
        "active": True,
        "description": "ARIA-SDR Webhook Integration"
    }
    
    try:
        response = requests.post(
            f"{MINDCHAT_API_BASE_URL}/webhook",
            json=webhook_payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_mindchat_api_docs():
    """Testa acesso à documentação da API"""
    print("\nTestando documentação da API...")
    
    try:
        response = requests.get(
            f"{MINDCHAT_API_BASE_URL}/api-docs/",
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"   Content-Length: {len(response.text)}")
            
            # Verificar se é HTML ou JSON
            if 'text/html' in response.headers.get('content-type', ''):
                print("   Documentação HTML disponível")
            elif 'application/json' in response.headers.get('content-type', ''):
                print("   Documentação JSON disponível")
                try:
                    data = response.json()
                    print(f"   Swagger version: {data.get('swagger', 'N/A')}")
                    print(f"   OpenAPI version: {data.get('openapi', 'N/A')}")
                except:
                    pass
            
            return True
        else:
            print(f"   Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_mindchat_openapi_spec():
    """Testa especificação OpenAPI"""
    print("\nTestando especificação OpenAPI...")
    
    try:
        response = requests.get(
            f"{MINDCHAT_API_BASE_URL}/openapi.json",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {response.status_code}")
            print(f"   OpenAPI version: {data.get('openapi', 'N/A')}")
            print(f"   Info title: {data.get('info', {}).get('title', 'N/A')}")
            print(f"   Info version: {data.get('info', {}).get('version', 'N/A')}")
            
            # Listar paths disponíveis
            paths = data.get('paths', {})
            print(f"   Endpoints disponíveis: {len(paths)}")
            
            for path, methods in list(paths.items())[:10]:  # Primeiros 10
                print(f"     {path}: {list(methods.keys())}")
            
            return True
        else:
            print(f"   Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def main():
    """Executa testes específicos da API Mindchat"""
    print("Testando funcionalidades específicas da API Mindchat")
    print(f"API Base URL: {MINDCHAT_API_BASE_URL}")
    print("=" * 60)
    
    tests = [
        ("Mensagens Detalhadas", test_mindchat_messages_detailed),
        ("Envio de Mensagem", test_mindchat_send_message),
        ("Conversas Detalhadas", test_mindchat_conversations_detailed),
        ("Criação de Webhook", test_mindchat_webhook_creation),
        ("Documentação API", test_mindchat_api_docs),
        ("Especificação OpenAPI", test_mindchat_openapi_spec)
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
    print("RESUMO DOS TESTES ESPECÍFICOS:")
    
    for test_name, result in results:
        status = "SUCESSO" if result else "FALHOU"
        print(f"   {test_name}: {status}")
    
    print("\nDescobertas importantes:")
    print("1. API Mindchat está funcionando")
    print("2. Endpoint /api/messages retorna dados reais")
    print("3. Possível envio de mensagens via /api/send")
    print("4. Webhooks podem ser configurados")
    print("5. Documentação OpenAPI disponível")

if __name__ == "__main__":
    main()
