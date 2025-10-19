from textwrap import dedent
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.memory.manager import MemoryManager
from agno.models.openai import OpenAIChat
from agno.os.app import AgentOS
from agno.os.interfaces.whatsapp import Whatsapp
from agno.tools.googlesearch import GoogleSearchTools

# Configuracao do banco de dados
agent_db = SqliteDb(db_file="tmp/aria_persistent_memory.db")

# Configuracao do modelo OpenAI
model = OpenAIChat(id="gpt-4o-mini")

# Gerenciador de memoria
memory_manager = MemoryManager(
    memory_capture_instructions=dedent("""
        Collect User's name,
        Collect Information about user's passion and hobbies,
        Collect Information about the users likes and dislikes,
        Collect information about what the user is doing with their life right now,
        Collect information about their business needs and volume requirements
    """),
    model=model,
)

# Agente ARIA-SDR personalizado
aria_agent = Agent(
    name="ARIA-SDR",
    model=model,
    tools=[GoogleSearchTools()],
    add_history_to_context=True,
    num_history_runs=3,
    add_datetime_to_context=True,
    markdown=True,
    db=agent_db,
    memory_manager=memory_manager,
    enable_agentic_memory=True,
    instructions=dedent("""
        Voce e a ARIA, Agente de Relacionamento Inteligente da AR Online.
        
        Suas responsabilidades:
        1. Atender clientes via WhatsApp e chat web
        2. Classificar volumetria de envios (alto/baixo volume)
        3. Roteamento inteligente para FAQ, agendamento ou loja
        4. Responder em portugues brasileiro de forma cordial e objetiva
        
        Regras de negocio:
        - Volume alto: >= 1200 mensagens/mes -> Agendamento
        - Volume baixo: < 1200 mensagens/mes -> Loja
        - Use contexto fornecido quando disponivel
        - Se nao souber algo, ofereca encaminhar ao time
        
        Primeiro se apresente e pergunte o nome do usuario, depois pergunte sobre:
        - Seus hobbies e interesses
        - O que gosta de fazer
        - Sobre o que gosta de conversar
        - Suas necessidades de negocio
        
        Use a ferramenta Google Search para encontrar informacoes atualizadas sobre os topicos da conversa.
        
        Sempre seja cordial, objetivo e profissional.
    """),
    debug_mode=True,
)

# Configurar AgentOS
agent_os = AgentOS(
    agents=[aria_agent],
    interfaces=[Whatsapp(agent=aria_agent)],
)

# Obter app FastAPI
app = agent_os.get_app()

if __name__ == "__main__":
    print("ARIA-SDR - Iniciando agente com memoria persistente")
    print("=" * 60)
    print(f"Agente: {aria_agent.name}")
    print(f"Modelo: {aria_agent.model}")
    print(f"Ferramentas: {len(aria_agent.tools)}")
    print("=" * 60)
    
    agent_os.serve(app="aria_agent_openai:app", reload=True)
