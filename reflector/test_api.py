#!/usr/bin/env python3
"""
ARIA-SDR Reflector - Exemplo de Uso
"""
import requests
import json

def test_aria_api():
    """Testa a API da ARIA"""
    base_url = "http://localhost:8000"
    
    # Teste de health check
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{base_url}/healthz")
        if response.status_code == 200:
            print("✅ Health check OK")
            print(f"   Resposta: {response.json()}")
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    
    # Teste de chat
    print("\n💬 Testando chat...")
    try:
        chat_data = {
            "message": "Olá! Como funciona a AR Online?",
            "agent": "aria-sdr"
        }
        
        response = requests.post(f"{base_url}/chat", json=chat_data)
        if response.status_code == 200:
            print("✅ Chat OK")
            print(f"   Resposta: {response.json()}")
        else:
            print(f"❌ Chat falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no chat: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    print("🧪 ARIA-SDR Reflector - Teste de API")
    print("=" * 50)
    
    if test_aria_api():
        print("\n🎉 Todos os testes passaram!")
        print("A ARIA está funcionando corretamente.")
    else:
        print("\n❌ Alguns testes falharam.")
        print("Verifique se o servidor está rodando: python main.py")

if __name__ == "__main__":
    main()
