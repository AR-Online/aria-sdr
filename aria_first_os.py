#!/usr/bin/env python3
"""
ARIA-SDR - Primeiro AgentOS
Baseado na documentação oficial: https://docs.agno.com/agent-os/creating-your-first-os
"""

import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.os import AgentOS

# Carregar variáveis de ambiente
load_dotenv()

# Criar agente ARIA-SDR
aria_assistant = Agent(
    name="ARIA-SDR",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "Você é a ARIA, Agente de Relacionamento Inteligente da AR Online.",
        "Suas responsabilidades:",
        "1. Atender clientes via WhatsApp e chat web",
        "2. Classificar volumetria de envios (alto/baixo volume)",
        "3. Roteamento inteligente para FAQ, agendamento ou loja",
        "4. Responder em português brasileiro de forma cordial e objetiva",
        "",
        "Regras de negócio:",
        "- Volume alto: >= 1200 mensagens/mês → Agendamento",
        "- Volume baixo: < 1200 mensagens/mês → Loja",
        "- Use contexto fornecido quando disponível",
        "- Se não souber algo, ofereça encaminhar ao time",
        "",
        "Sempre seja cordial, objetivo e profissional."
    ],
    markdown=True,
)

# Criar AgentOS
agent_os = AgentOS(
    id="aria-sdr-os",
    description="Sistema de Relacionamento Inteligente da AR Online",
    agents=[aria_assistant],
)

# Obter app FastAPI
app = agent_os.get_app()

if __name__ == "__main__":
    print("ARIA-SDR - Primeiro AgentOS")
    print("=" * 50)
    print("Baseado na documentação oficial do Agno")
    print("=" * 50)
    print(f"Agente: {aria_assistant.name}")
    print(f"Modelo: {aria_assistant.model}")
    print("=" * 50)
    print("\nRecursos disponíveis:")
    print("• Chat inteligente")
    print("• API RESTful")
    print("• Documentação automática")
    print("• Control Plane ready")
    print("=" * 50)
    print("\nEndpoints:")
    print("• App Interface: http://localhost:7777")
    print("• API Docs: http://localhost:7777/docs")
    print("• Config: http://localhost:7777/config")
    print("=" * 50)
    print("\nPara conectar ao Control Plane:")
    print("1. Acesse: https://platform.agno.com")
    print("2. Adicione novo OS: http://localhost:7777")
    print("3. Nome: ARIA-SDR")
    print("=" * 50)
    
    # Iniciar servidor (porta padrão 7777)
    agent_os.serve(app="aria_first_os:app", reload=True)
