#!/usr/bin/env python3
"""
ARIA-SDR Agent Configuration
Baseado na estrutura JSON fornecida
"""

import json
import os
from textwrap import dedent
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.memory.manager import MemoryManager
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.os.app import AgentOS
from agno.os.interfaces.whatsapp import Whatsapp
from agno.tools.googlesearch import GoogleSearchTools

def load_agent_config():
    """Carrega configuração do agente do arquivo JSON"""
    config_path = "agno/aria_agent_config.json"
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Configuração padrão se arquivo não existir
        return {
            "agents": [{
                "id": "aria-sdr-agent",
                "name": "ARIA-SDR",
                "db_id": "aria-sdr-db",
                "model": {
                    "name": "OpenAIChat",
                    "model": "gpt-4o-mini",
                    "provider": "OpenAI"
                }
            }]
        }

def create_database(config):
    """Cria banco de dados baseado na configuração"""
    db_config = config.get("database", {})
    
    if os.getenv("ENVIRONMENT") == "production" and db_config.get("production_type") == "postgresql":
        from agno.db.postgres import PostgresDb
        return PostgresDb(db_url=os.getenv("DATABASE_URL"))
    else:
        db_file = db_config.get("file", "tmp/aria_agents.db")
        return SqliteDb(db_file=db_file)

def create_model(model_config):
    """Cria modelo baseado na configuração"""
    provider = model_config.get("provider", "OpenAI")
    model_name = model_config.get("model", "gpt-4o-mini")
    
    if provider == "OpenAI":
        return OpenAIChat(id=model_name)
    elif provider == "Google":
        return Gemini(id=model_name)
    else:
        # Fallback para OpenAI
        return OpenAIChat(id="gpt-4o-mini")

def create_memory_manager(model):
    """Cria gerenciador de memória"""
    return MemoryManager(
        memory_capture_instructions=dedent("""
            Collect User's name,
            Collect Information about user's passion and hobbies,
            Collect Information about the users likes and dislikes,
            Collect information about what the user is doing with their life right now,
            Collect information about their business needs and volume requirements
        """),
        model=model,
    )

def create_aria_agent(config):
    """Cria agente ARIA-SDR baseado na configuração JSON"""
    
    agent_config = config["agents"][0]  # Primeiro agente
    
    # Criar componentes
    db = create_database(config)
    model = create_model(agent_config["model"])
    memory_manager = create_memory_manager(model)
    
    # Configurações do sistema
    system_config = agent_config.get("system_message", {})
    memory_config = agent_config.get("memory", {})
    
    # Instruções do agente
    instructions = system_config.get("instructions", dedent("""
        Você é a ARIA, Agente de Relacionamento Inteligente da AR Online.
        
        Suas responsabilidades:
        1. Atender clientes via WhatsApp e chat web
        2. Classificar volumetria de envios (alto/baixo volume)
        3. Roteamento inteligente para FAQ, agendamento ou loja
        4. Responder em português brasileiro de forma cordial e objetiva
        
        Regras de negócio:
        - Volume alto: >= 1200 mensagens/mês → Agendamento
        - Volume baixo: < 1200 mensagens/mês → Loja
        - Use contexto fornecido quando disponível
        - Se não souber algo, ofereça encaminhar ao time
        
        Sempre seja cordial, objetivo e profissional.
    """))
    
    # Criar agente
    agent = Agent(
        name=agent_config["name"],
        model=model,
        tools=[GoogleSearchTools()],
        db=db,
        memory_manager=memory_manager,
        enable_agentic_memory=memory_config.get("enable_agentic_memory", True),
        add_history_to_context=memory_config.get("add_history_to_context", True),
        num_history_runs=memory_config.get("num_history_runs", 3),
        add_datetime_to_context=system_config.get("add_datetime_to_context", True),
        markdown=system_config.get("markdown", True),
        instructions=instructions,
        debug_mode=os.getenv("APP_ENV") == "development",
    )
    
    return agent

def create_agent_os(config, agent):
    """Cria AgentOS com interfaces configuradas"""
    
    interfaces = []
    
    # Configurar interface WhatsApp se disponível
    whatsapp_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    if whatsapp_token:
        whatsapp_interface = Whatsapp(agent=agent)
        interfaces.append(whatsapp_interface)
    
    # Criar AgentOS
    agent_os = AgentOS(
        agents=[agent],
        interfaces=interfaces,
    )
    
    return agent_os

def main():
    """Função principal para criar e executar o agente"""
    
    print("ARIA-SDR - Inicializando agente baseado em configuração JSON")
    print("=" * 60)
    
    try:
        # Carregar configuração
        config = load_agent_config()
        print("✅ Configuração carregada")
        
        # Criar agente
        agent = create_aria_agent(config)
        print(f"✅ Agente {agent.name} criado")
        
        # Criar AgentOS
        agent_os = create_agent_os(config, agent)
        print("✅ AgentOS criado")
        
        # Obter app FastAPI
        app = agent_os.get_app()
        print("✅ App FastAPI criado")
        
        # Executar servidor
        print("\n🚀 Iniciando servidor...")
        agent_os.serve(app="aria_agent_from_config:app", reload=True)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
