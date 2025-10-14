#!/usr/bin/env python3
"""
Teste do AgentOS com Agente Mock
"""

import os
import sys
from dotenv import load_dotenv

def main():
    """Teste com agente mock"""
    
    print("ARIA-SDR - Teste do AgentOS com Agente Mock")
    print("=" * 50)
    
    # Carregar variaveis de ambiente
    load_dotenv()
    
    # Verificar OpenAI API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key.startswith("sk-your"):
        print("AVISO: OPENAI_API_KEY nao configurada")
        print("Configure no arquivo .env:")
        print("OPENAI_API_KEY=sk-sua-chave-aqui")
        print("\nContinuando com teste basico...")
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
        
        # Tentar criar agente com OpenAI se disponivel
        try:
            from agno.models.openai import OpenAIChat
            
            if openai_key and not openai_key.startswith("sk-your"):
                print("Criando agente com OpenAI...")
                model = OpenAIChat(id="gpt-4o-mini")
                
                agent = Agent(
                    id="test-agent",
                    name="Test Agent",
                    model=model,
                    db=db,
                    instructions="Voce e um agente de teste. Responda sempre 'OK'."
                )
                print("OK: Agente OpenAI criado")
                
                # Criar AgentOS com agente
                agent_os = AgentOS(agents=[agent])
                print("OK: AgentOS com agente criado")
                
                # Obter app
                app = agent_os.get_app()
                print("OK: App FastAPI criado")
                
                # Testar resposta do agente
                print("\nTestando resposta do agente...")
                response = agent.run("Responda apenas 'OK'")
                print(f"OK: Resposta do agente: {response.content}")
                
                print("\n" + "=" * 50)
                print("SUCESSO: AgentOS completo funcionando!")
                print("=" * 50)
                print("\nRecursos disponíveis:")
                print("• Agente OpenAI ativo")
                print("• Banco de dados SQLite")
                print("• API RESTful")
                print("• Interface web")
                print("\nPróximos passos:")
                print("1. Execute: python aria_sdr_api.py")
                print("2. Acesse: http://localhost:7777")
                print("3. Conecte ao Control Plane: https://platform.agno.com")
                
            else:
                raise ImportError("OpenAI não configurado")
                
        except ImportError as e:
            print(f"AVISO: OpenAI não disponível: {e}")
            print("Criando AgentOS sem agente...")
            
            # Criar AgentOS vazio para teste
            agent_os = AgentOS(agents=[])
            print("OK: AgentOS vazio criado")
            
            # Obter app
            app = agent_os.get_app()
            print("OK: App FastAPI criado")
            
            print("\n" + "=" * 50)
            print("SUCESSO: AgentOS basico funcionando!")
            print("=" * 50)
            print("\nPara funcionalidade completa:")
            print("1. Configure OPENAI_API_KEY no .env")
            print("2. Execute: python aria_sdr_api.py")
            print("3. Acesse: http://localhost:7777")
        
        return True
        
    except Exception as e:
        print(f"ERRO: Falha no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
