#!/usr/bin/env python3
"""
ARIA-SDR Reflector - Teste Simples
"""
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_imports():
    """Testa se todas as importações funcionam"""
    try:
        from agno.os import AgentOS
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
        from agno.tools import Toolkit
        print("✅ Importações AgentOS OK")
        return True
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False

def test_openai():
    """Testa conexão com OpenAI"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Teste simples de embedding
        response = client.embeddings.create(
            input="teste",
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        )
        print("✅ Conexão OpenAI OK")
        return True
    except Exception as e:
        print(f"❌ Erro OpenAI: {e}")
        return False

def test_supabase():
    """Testa conexão com Supabase"""
    try:
        import requests
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Variáveis Supabase não configuradas")
            return False
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
        }
        
        # Teste simples de conexão
        response = requests.get(f"{supabase_url}/rest/v1/rag_chunks?select=count", headers=headers)
        
        if response.status_code == 200:
            print("✅ Conexão Supabase OK")
            return True
        else:
            print(f"❌ Erro Supabase: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro Supabase: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 ARIA-SDR Reflector - Teste de Sistema")
    print("=" * 50)
    
    tests = [
        ("Importações", test_imports),
        ("OpenAI", test_openai),
        ("Supabase", test_supabase),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testando {test_name}...")
        if test_func():
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema pronto.")
        return 0
    else:
        print("❌ Alguns testes falharam. Verifique a configuração.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
