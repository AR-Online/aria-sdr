#!/usr/bin/env python3
"""
Teste Simples do AgentOS ARIA-SDR
"""

import os
import sys
from dotenv import load_dotenv

def main():
    """Teste simples do AgentOS"""
    
    print("ARIA-SDR - Teste Simples do AgentOS")
    print("=" * 50)
    
    # Carregar variaveis de ambiente
    load_dotenv()
    
    # Verificar OpenAI API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key.startswith("sk-your"):
        print("ERRO: OPENAI_API_KEY nao configurada")
        print("Configure no arquivo .env:")
        print("OPENAI_API_KEY=sk-sua-chave-aqui")
        sys.exit(1)
    
    print("OK: OPENAI_API_KEY configurada")
    
    # Testar imports basicos
    try:
        print("Testando imports basicos...")
        import agno
        print("OK: agno importado")
        
        from agno.agent import Agent
        print("OK: Agent importado")
        
        from agno.models.openai import OpenAIChat
        print("OK: OpenAIChat importado")
        
        from agno.os.app import AgentOS
        print("OK: AgentOS importado")
        
        print("\nTestando criacao do modelo...")
        model = OpenAIChat(id="gpt-4o-mini")
        print(f"OK: Modelo criado: {model}")
        
        print("\nTestando criacao do agente...")
        agent = Agent(
            name="ARIA-SDR-Test",
            model=model,
            instructions="Voce e a ARIA, agente de teste.",
        )
        print(f"OK: Agente criado: {agent.name}")
        
        print("\nTestando criacao do AgentOS...")
        agent_os = AgentOS(agents=[agent])
        print(f"OK: AgentOS criado")
        
        print("\nTestando resposta do agente...")
        response = agent.run("Responda apenas 'OK' se voce esta funcionando")
        print(f"OK: Resposta: {response.content}")
        
        print("\n" + "=" * 50)
        print("SUCESSO: AgentOS ARIA-SDR esta funcionando!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"ERRO: Falha no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
