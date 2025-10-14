#!/usr/bin/env python3
"""
Teste do Primeiro AgentOS ARIA-SDR
"""

import os
import sys
from dotenv import load_dotenv

def main():
    """Teste do primeiro AgentOS"""
    
    print("ARIA-SDR - Teste do Primeiro AgentOS")
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Verificar OpenAI API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key.startswith("sk-your"):
        print("ERRO: OPENAI_API_KEY não configurada")
        print("Configure no arquivo .env:")
        print("OPENAI_API_KEY=sk-sua-chave-aqui")
        return False
    
    print("OK: OPENAI_API_KEY configurada")
    
    # Testar imports
    try:
        print("\nTestando imports...")
        from agno.agent import Agent
        print("OK: Agent importado")
        
        from agno.models.openai import OpenAIChat
        print("OK: OpenAIChat importado")
        
        from agno.os import AgentOS
        print("OK: AgentOS importado")
        
        print("\nTestando criação do agente...")
        model = OpenAIChat(id="gpt-4o-mini")
        print(f"OK: Modelo criado: {model}")
        
        agent = Agent(
            name="ARIA-SDR-Test",
            model=model,
            instructions=["Você é a ARIA, agente de teste."],
            markdown=True,
        )
        print(f"OK: Agente criado: {agent.name}")
        
        print("\nTestando criação do AgentOS...")
        agent_os = AgentOS(
            id="aria-test-os",
            description="Teste do ARIA-SDR",
            agents=[agent],
        )
        print("OK: AgentOS criado")
        
        print("\nTestando app FastAPI...")
        app = agent_os.get_app()
        print("OK: App FastAPI criado")
        
        print("\nTestando resposta do agente...")
        response = agent.run("Responda apenas 'OK' se você está funcionando")
        print(f"OK: Resposta: {response.content}")
        
        print("\n" + "=" * 50)
        print("SUCESSO: Primeiro AgentOS funcionando!")
        print("=" * 50)
        print("\nPara executar:")
        print("python aria_first_os.py")
        print("\nPara conectar ao Control Plane:")
        print("1. Acesse: https://platform.agno.com")
        print("2. Adicione novo OS: http://localhost:7777")
        print("3. Nome: ARIA-SDR")
        
        return True
        
    except Exception as e:
        print(f"ERRO: Falha no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
