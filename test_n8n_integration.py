#!/usr/bin/env python3
"""
Script de teste para integração n8n
Testa a conexão e funcionalidade da ARIA-SDR com n8n
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

def load_env():
    """Carrega variáveis de ambiente do arquivo .env"""
    env_vars = {}
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        print("Arquivo .env não encontrado. Usando variáveis do sistema.")
    
    return env_vars

def test_aria_health():
    """Testa se a ARIA-SDR está funcionando"""
    print("🔍 Testando saúde da ARIA-SDR...")
    
    try:
        response = requests.get("http://localhost:8000/healthz", timeout=5)
        if response.status_code == 200:
            print("✅ ARIA-SDR está funcionando")
            return True
        else:
            print(f"❌ ARIA-SDR retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com ARIA-SDR: {e}")
        return False

def test_n8n_status(env_vars):
    """Testa status da integração n8n"""
    print("🔧 Testando status da integração n8n...")
    
    api_token = env_vars.get('FASTAPI_BEARER_TOKEN', 'dtransforma')
    
    try:
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            "http://localhost:8000/n8n/status",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status n8n: {data.get('status', 'unknown')}")
            print(f"   ARIA Status: {data.get('aria_status', 'unknown')}")
            print(f"   Webhook URL: {data.get('webhook_url', 'N/A')}")
            print(f"   Workflow ID: {data.get('workflow_id', 'N/A')}")
            
            return True
        else:
            print(f"❌ Erro ao obter status n8n: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar status n8n: {e}")
        return False

def test_n8n_webhook(env_vars):
    """Testa webhook do n8n com payload simulado"""
    print("📨 Testando webhook do n8n...")
    
    api_token = env_vars.get('FASTAPI_BEARER_TOKEN', 'dtransforma')
    workflow_id = env_vars.get('N8N_WORKFLOW_ID', '845ead21-31da-47d2-81fd-a1fe46dc34e8')
    
    # Simular payload do n8n
    test_payload = {
        "source": "n8n",
        "message": "Olá ARIA! Este é um teste de integração n8n.",
        "sender": "n8n_test_user",
        "channel": "n8n",
        "timestamp": datetime.now().isoformat(),
        "workflow_id": workflow_id,
        "execution_id": f"exec_{int(time.time())}",
        "metadata": {
            "test": True,
            "source": "test_script",
            "priority": "normal"
        }
    }
    
    try:
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "http://localhost:8000/n8n/webhook",
            json=test_payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Webhook n8n processado com sucesso")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Execution ID: {data.get('execution_id', 'N/A')}")
            
            if 'aria_response' in data:
                aria_resp = data['aria_response']
                print(f"   ARIA Response: {aria_resp.get('reply_text', 'N/A')[:50]}...")
            
            return True
        else:
            print(f"❌ Erro no webhook n8n: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar webhook n8n: {e}")
        return False

def test_n8n_external_webhook(env_vars):
    """Testa webhook externo do n8n"""
    print("🌐 Testando webhook externo do n8n...")
    
    webhook_url = env_vars.get('N8N_WEBHOOK_URL', 'https://n8n-inovacao.ar-infra.com.br/webhook-test/845ead21-31da-47d2-81fd-a1fe46dc34e8')
    
    # Simular payload para o webhook externo
    test_payload = {
        "message": "Teste de integração externa n8n",
        "sender": "external_test",
        "channel": "external",
        "metadata": {
            "test": True,
            "source": "aria_test_script"
        }
    }
    
    try:
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201, 202]:
            print(f"✅ Webhook externo n8n acessível")
            print(f"   Status: {response.status_code}")
            print(f"   URL: {webhook_url}")
            return True
        else:
            print(f"⚠️  Webhook externo retornou status {response.status_code}")
            print(f"   Resposta: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar webhook externo n8n: {e}")
        return False

def main():
    """Função principal do teste"""
    print("🚀 Teste de Integração n8n - ARIA-SDR")
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    env_vars = load_env()
    
    # Verificar variáveis essenciais
    required_vars = [
        'FASTAPI_BEARER_TOKEN',
        'N8N_WEBHOOK_URL',
        'N8N_WORKFLOW_ID'
    ]
    
    missing_vars = [var for var in required_vars if not env_vars.get(var)]
    if missing_vars:
        print(f"❌ Variáveis obrigatórias não encontradas: {', '.join(missing_vars)}")
        print("   Configure essas variáveis no arquivo .env")
        return False
    
    print(f"🔧 Webhook n8n: {env_vars.get('N8N_WEBHOOK_URL')}")
    print(f"🆔 Workflow ID: {env_vars.get('N8N_WORKFLOW_ID')}")
    print()
    
    # Executar testes
    tests = [
        ("Saúde da ARIA-SDR", lambda: test_aria_health()),
        ("Status n8n", lambda: test_n8n_status(env_vars)),
        ("Webhook n8n interno", lambda: test_n8n_webhook(env_vars)),
        ("Webhook n8n externo", lambda: test_n8n_external_webhook(env_vars))
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)  # Pausa entre testes
    
    # Resumo dos resultados
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Integração n8n funcionando.")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique a configuração.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
