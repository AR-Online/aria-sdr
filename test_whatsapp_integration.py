#!/usr/bin/env python3
"""
Script de teste para integração WhatsApp via Mindchat
Testa a conexão e funcionalidade da ARIA-SDR com WhatsApp
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

def test_whatsapp_status(env_vars):
    """Testa status da integração WhatsApp"""
    print("📱 Testando status da integração WhatsApp...")
    
    api_token = env_vars.get('FASTAPI_BEARER_TOKEN', 'dtransforma')
    
    try:
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            "http://localhost:8000/whatsapp/status",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status WhatsApp: {data.get('status', 'unknown')}")
            print(f"   ARIA Status: {data.get('aria_status', 'unknown')}")
            print(f"   Webhook URL: {data.get('webhook_url', 'N/A')}")
            
            if 'mindchat_status' in data:
                print(f"   Mindchat Status: {data['mindchat_status']}")
            
            return True
        else:
            print(f"❌ Erro ao obter status WhatsApp: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar status WhatsApp: {e}")
        return False

def test_whatsapp_webhook(env_vars):
    """Testa webhook do WhatsApp com mensagem simulada"""
    print("📨 Testando webhook do WhatsApp...")
    
    api_token = env_vars.get('FASTAPI_BEARER_TOKEN', 'dtransforma')
    whatsapp_number = env_vars.get('WHATSAPP_NUMBER', '+5516997918658')
    
    # Simular mensagem do WhatsApp
    test_message = {
        "from": whatsapp_number,
        "to": whatsapp_number,
        "message": "Olá ARIA! Este é um teste de integração WhatsApp.",
        "timestamp": datetime.now().isoformat(),
        "id": f"test_msg_{int(time.time())}",
        "type": "text"
    }
    
    try:
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "http://localhost:8000/whatsapp/webhook",
            json=test_message,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Webhook processado com sucesso")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Message ID: {data.get('message_id', 'N/A')}")
            return True
        else:
            print(f"❌ Erro no webhook WhatsApp: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar webhook WhatsApp: {e}")
        return False

def test_mindchat_connection(env_vars):
    """Testa conexão com Mindchat API"""
    print("🔗 Testando conexão com Mindchat...")
    
    api_token = env_vars.get('MINDCHAT_API_TOKEN')
    base_url = env_vars.get('MINDCHAT_API_BASE_URL', 'https://api-aronline.mindchatapp.com.br')
    
    if not api_token:
        print("❌ MINDCHAT_API_TOKEN não configurado")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        # Testar endpoint de status (assumindo que existe)
        response = requests.get(
            f"{base_url}/api/status",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Conexão com Mindchat estabelecida")
            return True
        elif response.status_code == 404:
            print("⚠️  Endpoint /api/status não encontrado, mas API está acessível")
            return True
        else:
            print(f"⚠️  Mindchat retornou status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao conectar com Mindchat: {e}")
        return False

def main():
    """Função principal do teste"""
    print("🚀 Teste de Integração WhatsApp - ARIA-SDR")
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    env_vars = load_env()
    
    # Verificar variáveis essenciais
    required_vars = [
        'FASTAPI_BEARER_TOKEN',
        'MINDCHAT_API_TOKEN',
        'MINDCHAT_API_BASE_URL',
        'WHATSAPP_NUMBER'
    ]
    
    missing_vars = [var for var in required_vars if not env_vars.get(var)]
    if missing_vars:
        print(f"❌ Variáveis obrigatórias não encontradas: {', '.join(missing_vars)}")
        print("   Configure essas variáveis no arquivo .env")
        return False
    
    print(f"📱 Número WhatsApp configurado: {env_vars.get('WHATSAPP_NUMBER')}")
    print(f"🔗 Mindchat API: {env_vars.get('MINDCHAT_API_BASE_URL')}")
    print()
    
    # Executar testes
    tests = [
        ("Saúde da ARIA-SDR", lambda: test_aria_health()),
        ("Status WhatsApp", lambda: test_whatsapp_status(env_vars)),
        ("Conexão Mindchat", lambda: test_mindchat_connection(env_vars)),
        ("Webhook WhatsApp", lambda: test_whatsapp_webhook(env_vars))
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
        print("🎉 Todos os testes passaram! Integração WhatsApp funcionando.")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique a configuração.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
