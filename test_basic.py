#!/usr/bin/env python3
"""
Teste Basico do AgentOS sem OpenAI
"""

import os
import sys
from dotenv import load_dotenv

def main():
    """Teste basico sem OpenAI"""
    
    print("ARIA-SDR - Teste Basico do AgentOS")
    print("=" * 50)
    
    # Carregar variaveis de ambiente
    load_dotenv()
    
    # Verificar OpenAI API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key.startswith("sk-your"):
        print("AVISO: OPENAI_API_KEY nao configurada")
        print("Configure no arquivo .env:")
        print("OPENAI_API_KEY=sk-sua-chave-aqui")
    else:
        print("OK: OPENAI_API_KEY configurada")
    
    # Testar imports basicos do Agno
    try:
        print("\nTestando imports basicos do Agno...")
        import agno
        print("OK: agno importado")
        
        from agno.agent import Agent
        print("OK: Agent importado")
        
        from agno.os.app import AgentOS
        print("OK: AgentOS importado")
        
        from agno.db.sqlite import SqliteDb
        print("OK: SqliteDb importado")
        
        print("\nTestando criacao de componentes basicos...")
        
        # Criar banco de dados
        db = SqliteDb(db_file="tmp/test.db")
        print("OK: Banco de dados criado")
        
        # Criar AgentOS basico (sem agente ainda)
        agent_os = AgentOS()
        print("OK: AgentOS criado")
        
        # Obter app
        app = agent_os.get_app()
        print("OK: App FastAPI criado")
        
        print("\n" + "=" * 50)
        print("SUCESSO: Componentes basicos do AgentOS funcionando!")
        print("=" * 50)
        print("\nPróximos passos:")
        print("1. Configure OPENAI_API_KEY no .env")
        print("2. Execute: python aria_sdr_api.py")
        print("3. Acesse: http://localhost:7777")
        print("4. Conecte ao Control Plane: https://platform.agno.com")
        
        return True
        
    except Exception as e:
        print(f"ERRO: Falha no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
