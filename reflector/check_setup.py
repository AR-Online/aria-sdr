#!/usr/bin/env python3
"""
ARIA-SDR Reflector - Script de Inicialização
"""
import os
import sys
import subprocess

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        import agno
        import openai
        import numpy
        import requests
        import uvicorn
        from dotenv import load_dotenv
        print("✅ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("Execute: pip install -r requirements.txt")
        return False

def check_env():
    """Verifica se o arquivo .env existe"""
    if not os.path.exists(".env"):
        print("❌ Arquivo .env não encontrado")
        print("Execute: cp env.example .env")
        print("Depois edite o arquivo .env com suas chaves")
        return False
    
    # Load .env to check variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f"your_{var.lower()}_here":
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variáveis não configuradas: {', '.join(missing_vars)}")
        print("Edite o arquivo .env com suas chaves reais")
        return False
    
    print("✅ Configuração do ambiente OK")
    return True

def main():
    """Função principal"""
    print("🚀 ARIA-SDR Reflector - Verificação de Sistema")
    print("=" * 50)
    
    # Verificar dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar configuração
    if not check_env():
        sys.exit(1)
    
    print("\n✅ Sistema pronto para execução!")
    print("Execute: python main.py")
    print("Servidor será iniciado em: http://localhost:8000")

if __name__ == "__main__":
    main()
