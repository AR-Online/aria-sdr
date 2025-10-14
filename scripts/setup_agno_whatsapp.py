#!/usr/bin/env python3
"""
Script para configurar variaveis de ambiente do Agno com WhatsApp
ARIA-SDR - Configuracao de Ambiente
"""

import os
import subprocess
import sys

def set_environment_variables():
    """Configura as variaveis de ambiente necessarias"""
    
    print("Configurando variaveis de ambiente para Agno + WhatsApp...")
    print("=" * 60)
    
    # Variaveis do WhatsApp
    whatsapp_vars = {
        "WHATSAPP_ACCESS_TOKEN": "your_whatsapp_access_token",
        "WHATSAPP_PHONE_NUMBER_ID": "your_phone_number_id", 
        "WHATSAPP_WEBHOOK_URL": "your_webhook_url",
        "WHATSAPP_VERIFY_TOKEN": "your_verify_token"
    }
    
    # Variaveis do Google
    google_vars = {
        "GOOGLE_API_KEY": "your_google_api_key",
        "GOOGLE_SEARCH_API_KEY": "your_google_search_api_key"
    }
    
    # Variaveis de ambiente
    env_vars = {
        "APP_ENV": "development"
    }
    
    # Configurar variaveis
    all_vars = {**whatsapp_vars, **google_vars, **env_vars}
    
    print("Variaveis a serem configuradas:")
    for key, default_value in all_vars.items():
        current_value = os.getenv(key, default_value)
        print(f"  {key}: {current_value}")
    
    print("\nPara configurar as variaveis, execute:")
    print("=" * 60)
    
    for key, default_value in all_vars.items():
        if default_value.startswith("your_"):
            print(f"export {key}=seu_valor_real_aqui")
        else:
            print(f"export {key}={default_value}")
    
    print("\nOu adicione ao arquivo .env:")
    print("=" * 60)
    
    for key, default_value in all_vars.items():
        if default_value.startswith("your_"):
            print(f"{key}=seu_valor_real_aqui")
        else:
            print(f"{key}={default_value}")

def check_dependencies():
    """Verifica se as dependencias estao instaladas"""
    
    print("\nVerificando dependencias...")
    print("=" * 60)
    
    try:
        import agno
        print("OK: Agno instalado")
    except ImportError:
        print("ERRO: Agno nao instalado - execute: pip install -U agno")
        return False
    
    try:
        from agno.models.google import Gemini
        print("OK: Google/Gemini disponivel")
    except ImportError:
        print("ERRO: Google/Gemini nao disponivel")
        return False
    
    try:
        from agno.os.interfaces.whatsapp import Whatsapp
        print("OK: WhatsApp interface disponivel")
    except ImportError:
        print("ERRO: WhatsApp interface nao disponivel")
        return False
    
    try:
        from agno.tools.googlesearch import GoogleSearchTools
        print("OK: Google Search tools disponivel")
    except ImportError:
        print("ERRO: Google Search tools nao disponivel")
        return False
    
    return True

def test_agent():
    """Testa se o agente pode ser criado"""
    
    print("\nTestando criacao do agente...")
    print("=" * 60)
    
    try:
        from agent_with_user_memory import personal_agent
        print("OK: Agente criado com sucesso")
        print(f"   Nome: {personal_agent.name}")
        print(f"   Modelo: {personal_agent.model}")
        print(f"   Ferramentas: {len(personal_agent.tools)}")
        return True
    except Exception as e:
        print(f"ERRO: Erro ao criar agente: {e}")
        return False

def main():
    """Funcao principal"""
    
    print("ARIA-SDR - Configuracao do Agno com WhatsApp")
    print("=" * 60)
    
    # Verificar dependencias
    if not check_dependencies():
        print("\nERRO: Dependencias faltando. Instale com: pip install -U agno")
        sys.exit(1)
    
    # Configurar variaveis
    set_environment_variables()
    
    # Testar agente
    if test_agent():
        print("\nOK: Configuracao concluida com sucesso!")
        print("\nPara executar o agente:")
        print("  python agent_with_user_memory.py")
    else:
        print("\nERRO: Problemas na configuracao do agente")
        sys.exit(1)

if __name__ == "__main__":
    main()
