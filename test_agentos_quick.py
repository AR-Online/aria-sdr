#!/usr/bin/env python3
"""
Teste Rapido do AgentOS ARIA-SDR
"""

import os
import sys
from dotenv import load_dotenv

def main():
    """Teste rapido do AgentOS"""
    
    print("ARIA-SDR - Teste Rapido do AgentOS")
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
    
    # Verificar dependencias
    try:
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
        from agno.os.app import AgentOS
        print("OK: Dependencias do Agno instaladas")
    except ImportError as e:
        print(f"ERRO: Dependencia faltando: {e}")
        print("Instale com: pip install -U agno")
        sys.exit(1)
    
    # Criar agente simples
    try:
        model = OpenAIChat(id="gpt-4o-mini")
        agent = Agent(
            name="ARIA-SDR-Test",
            model=model,
            instructions="Voce e a ARIA, agente de teste. Responda apenas 'OK' quando solicitado.",
        )
        
        agent_os = AgentOS(agents=[agent])
        app = agent_os.get_app()
        
        print("OK: AgentOS criado com sucesso")
        print(f"OK: Agente: {agent.name}")
        print(f"OK: Modelo: {agent.model}")
        
        # Testar resposta do agente
        response = agent.run("Responda apenas 'OK' se voce esta funcionando")
        print(f"OK: Resposta do agente: {response.content}")
        
        print("\n" + "=" * 50)
        print("SUCESSO: AgentOS ARIA-SDR esta funcionando!")
        print("=" * 50)
        print("\nPara conectar ao Control Plane:")
        print("1. Execute: python aria_agentos_optimized.py")
        print("2. Acesse: https://platform.agno.com")
        print("3. Adicione OS: http://localhost:7777")
        print("4. Nome: ARIA-SDR Development")
        
    except Exception as e:
        print(f"ERRO: Falha ao criar AgentOS: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
