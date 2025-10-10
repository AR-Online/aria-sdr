#!/usr/bin/env python3
"""
Script de verificação de variáveis de ambiente para ARIA-SDR
Verifica se todas as variáveis necessárias estão configuradas
"""

import os
import sys
from dotenv import load_dotenv

def check_env_vars():
    """Verifica se todas as variáveis de ambiente estão configuradas"""
    
    # Carrega o arquivo .env se existir
    load_dotenv()
    
    # Variáveis obrigatórias
    required_vars = {
        'FASTAPI_BEARER_TOKEN': 'Token de autenticação da API',
        'OPENAI_API_KEY': 'Chave da API OpenAI',
        'ASSISTANT_ID': 'ID do Assistant OpenAI',
        'SUPABASE_URL': 'URL do projeto Supabase',
        'SUPABASE_SERVICE_ROLE_KEY': 'Chave de serviço do Supabase',
    }
    
    # Variáveis opcionais (com valores padrão)
    optional_vars = {
        'API_HOST': '0.0.0.0',
        'API_PORT': '8000',
        'API_LOG_LEVEL': 'info',
        'ASSISTANT_TIMEOUT_SECONDS': '12',
        'EMBEDDING_MODEL': 'text-embedding-3-small',
        'EMBEDDING_DIM': '1536',
        'RAG_ENABLE': 'true',
        'RAG_ENDPOINT': 'http://127.0.0.1:8000/rag/query',
        'RAG_DEFAULT_SOURCE': 'faq',
        'VOLUME_ALTO_LIMIAR': '1200',
        'AGNO_ROUTING_WEBHOOK': 'https://agno.ar-infra.com.br/webhook/assist/routing',
        'AGNO_API_BASE_URL': 'https://agno.ar-infra.com.br/api/v1',
    }
    
    # Variáveis do Agno (precisam ser configuradas)
    agno_vars = {
        'AGNO_AUTH_TOKEN': 'Token de autenticação do Agno',
        'AGNO_BOT_ID': 'ID do bot no Agno',
    }
    
    # Variáveis do Cloudflare (já configuradas)
    cloudflare_vars = {
        'CLOUDFLARE_API_TOKEN': 'Token da API Cloudflare',
    }
    
    print("Verificando variaveis de ambiente...")
    print("=" * 50)
    
    # Verifica variáveis obrigatórias
    missing_required = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_required.append(f"ERRO {var}: {description}")
        else:
            print(f"OK {var}: {'*' * min(len(value), 20)}...")
    
    # Verifica variáveis opcionais
    print("\nVariaveis opcionais:")
    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        print(f"OK {var}: {value}")
    
    # Verifica variáveis do Agno
    print("\nVariaveis do Agno:")
    missing_agno = []
    for var, description in agno_vars.items():
        value = os.getenv(var)
        if not value:
            missing_agno.append(f"ERRO {var}: {description}")
        else:
            print(f"OK {var}: {'*' * min(len(value), 20)}...")
    
    # Verifica variáveis do Cloudflare
    print("\nVariaveis do Cloudflare:")
    for var, description in cloudflare_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"ERRO {var}: {description}")
        else:
            print(f"OK {var}: {'*' * min(len(value), 20)}...")
    
    # Resultado final
    print("\n" + "=" * 50)
    if missing_required:
        print("ERRO: Variaveis obrigatorias nao configuradas:")
        for var in missing_required:
            print(f"   {var}")
        return False
    
    if missing_agno:
        print("AVISO: Variaveis do Agno nao configuradas:")
        for var in missing_agno:
            print(f"   {var}")
        print("\nPara configurar:")
        print("   1. Copie config.env.example para .env")
        print("   2. Configure AGNO_AUTH_TOKEN e AGNO_BOT_ID")
        print("   3. Execute este script novamente")
        return False
    
    print("OK: Todas as variaveis estao configuradas!")
    print("Pronto para executar o ARIA-SDR!")
    return True

if __name__ == "__main__":
    success = check_env_vars()
    sys.exit(0 if success else 1)
