#!/usr/bin/env python3
"""
Script de Configuracao para Conectar ARIA-SDR ao Control Plane
Baseado na documentacao oficial: https://docs.agno.com/agent-os/connecting-your-os
"""

import os
import sys
import subprocess
import webbrowser
from dotenv import load_dotenv

def print_header():
    """Imprime cabecalho do script"""
    print("=" * 80)
    print("ARIA-SDR - Configuracao para Control Plane")
    print("Documentacao: https://docs.agno.com/agent-os/connecting-your-os")
    print("=" * 80)

def check_environment():
    """Verifica configuracao do ambiente"""
    print("\n1. Verificando configuracao do ambiente...")
    print("-" * 50)
    
    # Carregar variaveis de ambiente
    load_dotenv()
    
    # Variaveis obrigatorias
    required_vars = {
        "OPENAI_API_KEY": "Chave da API OpenAI",
    }
    
    # Variaveis opcionais
    optional_vars = {
        "WHATSAPP_ACCESS_TOKEN": "Token de acesso WhatsApp",
        "WHATSAPP_PHONE_NUMBER_ID": "ID do numero WhatsApp",
        "GOOGLE_API_KEY": "Chave da API Google",
        "DATABASE_URL": "URL do banco PostgreSQL (producao)",
        "MODEL_PROVIDER": "Provedor do modelo (openai/google)",
        "MODEL_ID": "ID do modelo",
        "HOST": "Host do servidor",
        "PORT": "Porta do servidor",
    }
    
    missing_required = []
    configured_optional = []
    
    # Verificar variaveis obrigatorias
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value.startswith("your_") or value.startswith("seu_"):
            missing_required.append(f"  ERRO: {var}: {description}")
        else:
            print(f"  OK: {var}: {description}")
    
    # Verificar variaveis opcionais
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value and not value.startswith("your_") and not value.startswith("seu_"):
            configured_optional.append(f"  OK: {var}: {description}")
    
    if missing_required:
        print(f"\nERRO: Variaveis obrigatorias nao configuradas:")
        for var in missing_required:
            print(var)
        return False
    
    if configured_optional:
        print(f"\nOK: Variaveis opcionais configuradas:")
        for var in configured_optional:
            print(var)
    
    return True

def check_dependencies():
    """Verifica dependencias instaladas"""
    print("\n2. Verificando dependencias...")
    print("-" * 50)
    
    dependencies = [
        ("agno", "Framework Agno"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Servidor ASGI"),
    ]
    
    missing_deps = []
    
    for package, description in dependencies:
        try:
            __import__(package)
            print(f"  OK: {package}: {description}")
        except ImportError:
            missing_deps.append(f"  ERRO: {package}: {description}")
    
    if missing_deps:
        print(f"\nERRO: Dependencias nao instaladas:")
        for dep in missing_deps:
            print(dep)
        print("\nInstale com: pip install -U agno fastapi uvicorn")
        return False
    
    return True

def start_agentos():
    """Inicia o AgentOS"""
    print("\n3. Iniciando AgentOS...")
    print("-" * 50)
    
    # Configuracoes padrao
    host = os.getenv("HOST", "localhost")
    port = os.getenv("PORT", "7777")
    
    print(f"  Host: {host}")
    print(f"  Porta: {port}")
    print(f"  Endpoint: http://{host}:{port}")
    
    try:
        # Importar e iniciar AgentOS
        from aria_agentos_optimized import aria_agentos
        
        print("\n  Iniciando servidor...")
        print("  Para parar: Ctrl+C")
        print("  Para recarregar: Salve qualquer arquivo")
        
        # Iniciar servidor
        aria_agentos.serve(host=host, port=int(port), reload=True)
        
    except KeyboardInterrupt:
        print("\n  Servidor parado pelo usuario")
    except Exception as e:
        print(f"\n  ERRO: Erro ao iniciar servidor: {e}")
        return False
    
    return True

def show_connection_instructions():
    """Mostra instrucoes para conectar ao Control Plane"""
    print("\n4. Instrucoes para conectar ao Control Plane")
    print("-" * 50)
    
    host = os.getenv("HOST", "localhost")
    port = os.getenv("PORT", "7777")
    endpoint = f"http://{host}:{port}"
    
    print(f"""
PASSO A PASSO:

1. Acesse: https://platform.agno.com
2. Faca login na sua conta Agno
3. Clique no botao "+" ao lado de "Add new OS"
4. Selecione "Local" para desenvolvimento
5. Endpoint URL: {endpoint}
6. OS Name: ARIA-SDR Development
7. Tags: development, aria-sdr, whatsapp
8. Clique em "CONNECT"

OK: Apos conectar, voce podera:
   • Conversar com o agente ARIA-SDR
   • Gerenciar conhecimento
   • Monitorar sessoes
   • Configurar memoria
""")

def open_control_plane():
    """Abre o Control Plane no navegador"""
    print("\n5. Abrindo Control Plane...")
    print("-" * 50)
    
    try:
        webbrowser.open("https://platform.agno.com")
        print("  Control Plane aberto no navegador")
    except Exception as e:
        print(f"  AVISO: Nao foi possivel abrir automaticamente: {e}")
        print("  Acesse manualmente: https://platform.agno.com")

def test_agentos_connection():
    """Testa se o AgentOS esta funcionando"""
    print("\n6. Testando conexao do AgentOS...")
    print("-" * 50)
    
    try:
        import requests
        host = os.getenv("HOST", "localhost")
        port = os.getenv("PORT", "7777")
        endpoint = f"http://{host}:{port}"
        
        # Testar endpoint de health
        response = requests.get(f"{endpoint}/health", timeout=5)
        if response.status_code == 200:
            print(f"  OK: AgentOS respondendo em {endpoint}")
            return True
        else:
            print(f"  ERRO: AgentOS retornou status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ERRO: Nao foi possivel conectar ao AgentOS")
        print(f"  Certifique-se de que o servidor esta rodando em {endpoint}")
        return False
    except ImportError:
        print("  AVISO: requests nao instalado - instale com: pip install requests")
        return False
    except Exception as e:
        print(f"  ERRO: Erro ao testar conexao: {e}")
        return False

def main():
    """Funcao principal"""
    
    print_header()
    
    # Verificar configuracao
    if not check_environment():
        print("\nERRO: Configure as variaveis obrigatorias no arquivo .env")
        sys.exit(1)
    
    # Verificar dependencias
    if not check_dependencies():
        print("\nERRO: Instale as dependencias necessarias")
        sys.exit(1)
    
    # Mostrar instrucoes
    show_connection_instructions()
    
    # Perguntar se quer abrir Control Plane
    try:
        response = input("\nAbrir Control Plane no navegador? (s/n): ").lower()
        if response in ['s', 'sim', 'y', 'yes']:
            open_control_plane()
    except KeyboardInterrupt:
        print("\nOperacao cancelada")
        sys.exit(0)
    
    # Perguntar se quer iniciar AgentOS
    try:
        response = input("\nIniciar AgentOS agora? (s/n): ").lower()
        if response in ['s', 'sim', 'y', 'yes']:
            start_agentos()
        else:
            print("\nPara iniciar manualmente:")
            print("   python aria_agentos_optimized.py")
    except KeyboardInterrupt:
        print("\nOperacao cancelada")
        sys.exit(0)

if __name__ == "__main__":
    main()
