#!/usr/bin/env python3
"""
Script de Configuração para Conectar ARIA-SDR ao Control Plane
Baseado na documentação oficial: https://docs.agno.com/agent-os/connecting-your-os
"""

import os
import sys
import subprocess
import webbrowser
from dotenv import load_dotenv

def print_header():
    """Imprime cabeçalho do script"""
    print("=" * 80)
    print("ARIA-SDR - Configuração para Control Plane")
    print("Documentação: https://docs.agno.com/agent-os/connecting-your-os")
    print("=" * 80)

def check_environment():
    """Verifica configuração do ambiente"""
    print("\n1. Verificando configuração do ambiente...")
    print("-" * 50)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Variáveis obrigatórias
    required_vars = {
        "OPENAI_API_KEY": "Chave da API OpenAI",
        "WHATSAPP_ACCESS_TOKEN": "Token de acesso WhatsApp (opcional)",
        "WHATSAPP_PHONE_NUMBER_ID": "ID do número WhatsApp (opcional)",
    }
    
    # Variáveis opcionais
    optional_vars = {
        "GOOGLE_API_KEY": "Chave da API Google",
        "DATABASE_URL": "URL do banco PostgreSQL (produção)",
        "MODEL_PROVIDER": "Provedor do modelo (openai/google)",
        "MODEL_ID": "ID do modelo",
        "HOST": "Host do servidor",
        "PORT": "Porta do servidor",
    }
    
    missing_required = []
    configured_optional = []
    
    # Verificar variáveis obrigatórias
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value.startswith("your_") or value.startswith("seu_"):
            missing_required.append(f"  ❌ {var}: {description}")
        else:
            print(f"  ✅ {var}: {description}")
    
    # Verificar variáveis opcionais
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value and not value.startswith("your_") and not value.startswith("seu_"):
            configured_optional.append(f"  ✅ {var}: {description}")
    
    if missing_required:
        print(f"\n❌ Variáveis obrigatórias não configuradas:")
        for var in missing_required:
            print(var)
        return False
    
    if configured_optional:
        print(f"\n✅ Variáveis opcionais configuradas:")
        for var in configured_optional:
            print(var)
    
    return True

def check_dependencies():
    """Verifica dependências instaladas"""
    print("\n2. Verificando dependências...")
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
            print(f"  ✅ {package}: {description}")
        except ImportError:
            missing_deps.append(f"  ❌ {package}: {description}")
    
    if missing_deps:
        print(f"\n❌ Dependências não instaladas:")
        for dep in missing_deps:
            print(dep)
        print("\nInstale com: pip install -U agno fastapi uvicorn")
        return False
    
    return True

def start_agentos():
    """Inicia o AgentOS"""
    print("\n3. Iniciando AgentOS...")
    print("-" * 50)
    
    # Configurações padrão
    host = os.getenv("HOST", "localhost")
    port = os.getenv("PORT", "7777")
    
    print(f"  🌐 Host: {host}")
    print(f"  🔌 Porta: {port}")
    print(f"  🔗 Endpoint: http://{host}:{port}")
    
    try:
        # Importar e iniciar AgentOS
        from aria_agentos_optimized import aria_agentos
        
        print("\n  🚀 Iniciando servidor...")
        print("  📋 Para parar: Ctrl+C")
        print("  🔄 Para recarregar: Salve qualquer arquivo")
        
        # Iniciar servidor
        aria_agentos.serve(host=host, port=int(port), reload=True)
        
    except KeyboardInterrupt:
        print("\n  ⏹️ Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n  ❌ Erro ao iniciar servidor: {e}")
        return False
    
    return True

def show_connection_instructions():
    """Mostra instruções para conectar ao Control Plane"""
    print("\n4. Instruções para conectar ao Control Plane")
    print("-" * 50)
    
    host = os.getenv("HOST", "localhost")
    port = os.getenv("PORT", "7777")
    endpoint = f"http://{host}:{port}"
    
    print(f"""
📋 PASSO A PASSO:

1. 🌐 Acesse: https://platform.agno.com
2. 👤 Faça login na sua conta Agno
3. ➕ Clique no botão "+" ao lado de "Add new OS"
4. 🏠 Selecione "Local" para desenvolvimento
5. 🔗 Endpoint URL: {endpoint}
6. 📝 OS Name: ARIA-SDR Development
7. 🏷️ Tags: development, aria-sdr, whatsapp
8. 🔗 Clique em "CONNECT"

✅ Após conectar, você poderá:
   • Conversar com o agente ARIA-SDR
   • Gerenciar conhecimento
   • Monitorar sessões
   • Configurar memória
""")

def open_control_plane():
    """Abre o Control Plane no navegador"""
    print("\n5. Abrindo Control Plane...")
    print("-" * 50)
    
    try:
        webbrowser.open("https://platform.agno.com")
        print("  🌐 Control Plane aberto no navegador")
    except Exception as e:
        print(f"  ⚠️ Não foi possível abrir automaticamente: {e}")
        print("  🌐 Acesse manualmente: https://platform.agno.com")

def main():
    """Função principal"""
    
    print_header()
    
    # Verificar configuração
    if not check_environment():
        print("\n❌ Configure as variáveis obrigatórias no arquivo .env")
        sys.exit(1)
    
    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Instale as dependências necessárias")
        sys.exit(1)
    
    # Mostrar instruções
    show_connection_instructions()
    
    # Perguntar se quer abrir Control Plane
    try:
        response = input("\n🌐 Abrir Control Plane no navegador? (s/n): ").lower()
        if response in ['s', 'sim', 'y', 'yes']:
            open_control_plane()
    except KeyboardInterrupt:
        print("\n⏹️ Operação cancelada")
        sys.exit(0)
    
    # Perguntar se quer iniciar AgentOS
    try:
        response = input("\n🚀 Iniciar AgentOS agora? (s/n): ").lower()
        if response in ['s', 'sim', 'y', 'yes']:
            start_agentos()
        else:
            print("\n📋 Para iniciar manualmente:")
            print("   python aria_agentos_optimized.py")
    except KeyboardInterrupt:
        print("\n⏹️ Operação cancelada")
        sys.exit(0)

if __name__ == "__main__":
    main()
