#!/usr/bin/env python3
"""
Script de teste para webhook GitLab da ARIA-SDR
Testa os endpoints de webhook e notificações WhatsApp
"""

import json
import requests
import os
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"  # URL da API ARIA
GITLAB_WEBHOOK_TOKEN = os.getenv("GITLAB_WEBHOOK_TOKEN", "dtransforma2026")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "+5516997918658")

def test_webhook_health():
    """Testa o health check do webhook"""
    print("🔍 Testando health check do webhook...")
    
    try:
        response = requests.get(f"{BASE_URL}/webhook/gitlab/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check OK: {data['status']}")
            print(f"   Service: {data['service']}")
            print(f"   Version: {data['version']}")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def test_pipeline_webhook():
    """Testa webhook de pipeline"""
    print("\n🔍 Testando webhook de pipeline...")
    
    payload = {
        "event_type": "pipeline",
        "project_name": "aria-sdr",
        "project_id": "123",
        "pipeline_status": "success",
        "pipeline_id": "456",
        "commit_sha": "abc123def456",
        "commit_message": "feat: adiciona integração GitLab webhook",
        "branch": "main",
        "user_name": "Louisa Rached",
        "user_email": "louisa@ar-online.com.br",
        "webhook_url": "https://gitlab.com/lourealiza/aria-sdr",
        "timestamp": datetime.now().isoformat(),
        "aria_action": "pipeline_notification"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GITLAB_WEBHOOK_TOKEN}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/gitlab/aria",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pipeline webhook OK: {data['status']}")
            print(f"   Event: {data['event_type']}")
            print(f"   Message: {data['message']}")
            return True
        else:
            print(f"❌ Pipeline webhook falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no pipeline webhook: {e}")
        return False

def test_deployment_webhook():
    """Testa webhook de deployment"""
    print("\n🔍 Testando webhook de deployment...")
    
    payload = {
        "event_type": "deployment",
        "project_name": "aria-sdr",
        "environment": "production",
        "deployment_status": "success",
        "deployment_id": "789",
        "commit_sha": "abc123def456",
        "commit_message": "feat: adiciona integração GitLab webhook",
        "branch": "main",
        "user_name": "Louisa Rached",
        "deployment_url": "https://api.ar-online.com.br",
        "timestamp": datetime.now().isoformat(),
        "aria_action": "deployment_notification"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GITLAB_WEBHOOK_TOKEN}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/gitlab/aria",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Deployment webhook OK: {data['status']}")
            print(f"   Event: {data['event_type']}")
            print(f"   Message: {data['message']}")
            return True
        else:
            print(f"❌ Deployment webhook falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no deployment webhook: {e}")
        return False

def test_merge_request_webhook():
    """Testa webhook de merge request"""
    print("\n🔍 Testando webhook de merge request...")
    
    payload = {
        "event_type": "merge_request",
        "project_name": "aria-sdr",
        "merge_request_id": "101",
        "merge_request_title": "feat: integração GitLab webhook",
        "merge_request_state": "opened",
        "source_branch": "feature/gitlab-webhook",
        "target_branch": "main",
        "author_name": "Louisa Rached",
        "author_email": "louisa@ar-online.com.br",
        "webhook_url": "https://gitlab.com/lourealiza/aria-sdr/-/merge_requests/101",
        "timestamp": datetime.now().isoformat(),
        "aria_action": "merge_request_notification"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GITLAB_WEBHOOK_TOKEN}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/gitlab/aria",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Merge Request webhook OK: {data['status']}")
            print(f"   Event: {data['event_type']}")
            print(f"   Message: {data['message']}")
            return True
        else:
            print(f"❌ Merge Request webhook falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no merge request webhook: {e}")
        return False

def test_push_webhook():
    """Testa webhook de push"""
    print("\n🔍 Testando webhook de push...")
    
    payload = {
        "event_type": "push",
        "project_name": "aria-sdr",
        "commit_count": "3",
        "commit_sha": "abc123def456",
        "commit_message": "feat: adiciona integração GitLab webhook",
        "branch": "main",
        "user_name": "Louisa Rached",
        "user_email": "louisa@ar-online.com.br",
        "webhook_url": "https://gitlab.com/lourealiza/aria-sdr",
        "timestamp": datetime.now().isoformat(),
        "aria_action": "push_notification"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GITLAB_WEBHOOK_TOKEN}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/gitlab/aria",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Push webhook OK: {data['status']}")
            print(f"   Event: {data['event_type']}")
            print(f"   Message: {data['message']}")
            return True
        else:
            print(f"❌ Push webhook falhou: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no push webhook: {e}")
        return False

def test_webhook_auth():
    """Testa autenticação do webhook"""
    print("\n🔍 Testando autenticação do webhook...")
    
    payload = {
        "aria_action": "pipeline_notification",
        "project_name": "aria-sdr-test"
    }
    
    # Teste sem token
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/gitlab/aria",
            json=payload
        )
        
        if response.status_code == 401:
            print("✅ Autenticação sem token falhou corretamente")
        else:
            print(f"❌ Autenticação sem token deveria falhar: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de autenticação: {e}")
        return False
    
    # Teste com token inválido
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer token_invalido"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/gitlab/aria",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 401:
            print("✅ Autenticação com token inválido falhou corretamente")
            return True
        else:
            print(f"❌ Autenticação com token inválido deveria falhar: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de autenticação: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes do webhook GitLab ARIA-SDR")
    print(f"📡 URL Base: {BASE_URL}")
    print(f"🔑 Token: {GITLAB_WEBHOOK_TOKEN[:10]}...")
    print(f"📱 WhatsApp: {WHATSAPP_NUMBER}")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_webhook_health),
        ("Autenticação", test_webhook_auth),
        ("Pipeline", test_pipeline_webhook),
        ("Deployment", test_deployment_webhook),
        ("Merge Request", test_merge_request_webhook),
        ("Push", test_push_webhook)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Webhook GitLab está funcionando!")
    else:
        print("⚠️  Alguns testes falharam. Verifique a configuração.")
    
    print("\n📋 Próximos passos:")
    print("1. Configure o webhook no GitLab:")
    print(f"   URL: {BASE_URL}/webhook/gitlab/aria")
    print(f"   Token: {GITLAB_WEBHOOK_TOKEN}")
    print("2. Selecione os eventos desejados")
    print("3. Use os templates personalizados da documentação")
    print("4. Teste com eventos reais do GitLab")

if __name__ == "__main__":
    main()
