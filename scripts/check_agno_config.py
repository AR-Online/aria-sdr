#!/usr/bin/env python3
"""
Script para verificar configuração das variáveis do Agno
ARIA-SDR - Verificação de Integridade
"""

import os
import sys
from typing import Dict, List, Tuple

def check_agno_configuration() -> Tuple[bool, List[str], List[str]]:
    """
    Verifica se as variáveis críticas do Agno estão configuradas
    
    Returns:
        Tuple[bool, List[str], List[str]]: (success, warnings, errors)
    """
    errors = []
    warnings = []
    
    # Variáveis críticas do Agno
    critical_vars = {
        'AGNO_AUTH_TOKEN': 'Token de autenticação do Agno',
        'AGNO_BOT_ID': 'ID do bot no Agno'
    }
    
    # Verificar variáveis críticas
    for var_name, description in critical_vars.items():
        value = os.getenv(var_name, '')
        
        if not value or value.strip() == '':
            errors.append(f"ERRO: {var_name}: {description} - NAO CONFIGURADO")
        elif value.startswith('seu_') or value.startswith('your_'):
            errors.append(f"ERRO: {var_name}: {description} - VALOR PLACEHOLDER")
        else:
            print(f"OK: {var_name}: {description} - CONFIGURADO")
    
    # Verificar outras variáveis importantes
    important_vars = {
        'AGNO_API_BASE_URL': 'URL base da API do Agno',
        'AGNO_ROUTING_WEBHOOK': 'Webhook de routing do Agno'
    }
    
    for var_name, description in important_vars.items():
        value = os.getenv(var_name, '')
        
        if not value or value.strip() == '':
            warnings.append(f"AVISO: {var_name}: {description} - NAO CONFIGURADO")
        else:
            print(f"OK: {var_name}: {description} - CONFIGURADO")
    
    # Verificar variáveis já configuradas
    configured_vars = {
        'FASTAPI_BEARER_TOKEN': 'Token de autenticação FastAPI',
        'OPENAI_API_KEY': 'Chave da API OpenAI',
        'SUPABASE_URL': 'URL do Supabase',
        'CLOUDFLARE_API_TOKEN': 'Token da API Cloudflare',
        'MINDCHAT_API_TOKEN': 'Token da API Mindchat'
    }
    
    for var_name, description in configured_vars.items():
        value = os.getenv(var_name, '')
        
        if not value or value.strip() == '':
            warnings.append(f"AVISO: {var_name}: {description} - NAO CONFIGURADO")
        else:
            print(f"OK: {var_name}: {description} - CONFIGURADO")
    
    success = len(errors) == 0
    
    return success, warnings, errors

def print_summary(success: bool, warnings: List[str], errors: List[str]) -> None:
    """Imprime resumo da verificação"""
    print("\n" + "="*60)
    print("RESUMO DA VERIFICAÇÃO DE CONFIGURAÇÃO AGNO")
    print("="*60)
    
    if errors:
        print(f"\nERROS CRITICOS ({len(errors)}):")
        for error in errors:
            print(f"  {error}")
    
    if warnings:
        print(f"\nAVISOS ({len(warnings)}):")
        for warning in warnings:
            print(f"  {warning}")
    
    if success:
        print(f"\nSUCESSO: Todas as variaveis criticas estao configuradas!")
        print("Sistema Agno pronto para funcionar")
    else:
        print(f"\nFALHA: {len(errors)} variaveis criticas nao configuradas")
        print("Sistema Agno NAO funcionara ate serem configuradas")
    
    print("\n" + "="*60)

def main():
    """Função principal"""
    print("Verificando configuração das variáveis do Agno...")
    print("ARIA-SDR - Sistema de Verificação de Integridade")
    print("-" * 60)
    
    # Carregar variáveis do .env se existir
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Arquivo .env carregado")
    except ImportError:
        print("python-dotenv nao instalado, usando apenas variaveis do sistema")
    except Exception as e:
        print(f"Erro ao carregar .env: {e}")
    
    # Verificar configuração
    success, warnings, errors = check_agno_configuration()
    
    # Imprimir resumo
    print_summary(success, warnings, errors)
    
    # Código de saída
    if success:
        print("\nVerificacao concluida com sucesso!")
        sys.exit(0)
    else:
        print("\nVerificacao falhou - configure as variaveis criticas")
        sys.exit(1)

if __name__ == "__main__":
    main()
