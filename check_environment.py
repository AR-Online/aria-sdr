#!/usr/bin/env python3
"""
Script de verificação de ambiente para ARIA-SDR
Verifica se todas as variáveis de ambiente necessárias estão configuradas
"""

import os
import sys
from typing import Dict, List, Tuple

def check_env_vars() -> Tuple[bool, List[str]]:
    """Verifica se as variáveis de ambiente necessárias estão configuradas"""
    
    required_vars = {
        'FASTAPI_BEARER_TOKEN': 'Token de autenticação da API',
        'API_HOST': 'Host da API (padrão: 0.0.0.0)',
        'API_PORT': 'Porta da API (padrão: 8000)',
    }
    
    optional_vars = {
        'OPENAI_API_KEY': 'Chave da API OpenAI para Assistants/RAG',
        'ASSISTANT_ID': 'ID do Assistant OpenAI',
        'SUPABASE_URL': 'URL do projeto Supabase',
        'SUPABASE_SERVICE_ROLE_KEY': 'Chave de serviço do Supabase',
        'CLOUDFLARE_API_TOKEN': 'Token da API Cloudflare',
        'MINDCHAT_API_TOKEN': 'Token da API Mindchat',
        'MINDCHAT_API_BASE_URL': 'URL base da API Mindchat',
    }
    
    missing_required = []
    missing_optional = []
    
    # Verificar variáveis obrigatórias
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_required.append(f"{var}: {description}")
    
    # Verificar variáveis opcionais
    for var, description in optional_vars.items():
        if not os.getenv(var):
            missing_optional.append(f"{var}: {description}")
    
    return len(missing_required) == 0, missing_required + missing_optional

def check_openai_config() -> bool:
    """Verifica se a configuração do OpenAI está correta"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("⚠️  OPENAI_API_KEY não configurada")
        return False
    
    if api_key.startswith('sk-proj-your-') or 'your-' in api_key:
        print("❌ OPENAI_API_KEY parece ser um placeholder")
        return False
    
    if len(api_key) < 20:
        print("❌ OPENAI_API_KEY parece muito curta")
        return False
    
    print("✅ OPENAI_API_KEY configurada corretamente")
    return True

def check_supabase_config() -> bool:
    """Verifica se a configuração do Supabase está correta"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not key:
        print("⚠️  Configuração do Supabase incompleta")
        return False
    
    if 'your-project' in url or 'your-' in key:
        print("❌ Configuração do Supabase parece ser placeholder")
        return False
    
    print("✅ Configuração do Supabase OK")
    return True

def main():
    """Função principal de verificação"""
    print("🔍 Verificando configuração do ambiente ARIA-SDR...\n")
    
    # Verificar variáveis de ambiente
    env_ok, missing_vars = check_env_vars()
    
    if not env_ok:
        print("❌ Variáveis de ambiente obrigatórias faltando:")
        for var in missing_vars:
            if 'obrigatórias' in str(missing_vars):
                print(f"   - {var}")
        print()
    
    # Verificar configurações específicas
    openai_ok = check_openai_config()
    supabase_ok = check_supabase_config()
    
    # Resumo
    print("\n📋 Resumo da verificação:")
    print(f"   Variáveis de ambiente: {'✅' if env_ok else '❌'}")
    print(f"   OpenAI: {'✅' if openai_ok else '❌'}")
    print(f"   Supabase: {'✅' if supabase_ok else '❌'}")
    
    if env_ok and openai_ok and supabase_ok:
        print("\n🎉 Todas as configurações estão corretas!")
        return 0
    else:
        print("\n⚠️  Algumas configurações precisam ser ajustadas.")
        print("   Consulte o arquivo env.template para referência.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
