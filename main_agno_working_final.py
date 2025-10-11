# main_agno_working_final.py - ARIA-SDR com AgentOS funcionando
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Configuration
AGNO_AUTH_TOKEN = os.getenv("AGNO_AUTH_TOKEN", "")
AGNO_BOT_ID = os.getenv("AGNO_BOT_ID", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

print("Configurando ARIA-SDR AgentOS...")

# Setup the database
db = SqliteDb(id="aria-db", db_file="tmp/aria.db")

# Setup ARIA agent sem modelo especÃ­fico
aria_agent = Agent(
    id="aria-sdr-agent",
    name="ARIA-SDR",
    db=db,
    markdown=True,
    instructions="""VocÃª Ã© a ARIA, Agente de Relacionamento Inteligente da AR Online.

Suas responsabilidades:
1. Atender clientes via WhatsApp e chat web
2. Classificar volumetria de envios (alto/baixo volume)
3. Roteamento inteligente para FAQ, agendamento ou loja
4. Responder em portuguÃªs brasileiro de forma cordial e objetiva

Regras de negÃ³cio:
- Volume alto: >= 1200 mensagens/mÃªs â†’ Agendamento
- Volume baixo: < 1200 mensagens/mÃªs â†’ Loja
- Use contexto fornecido quando disponÃ­vel
- Se nÃ£o souber algo, ofereÃ§a encaminhar ao time

Sempre seja cordial, objetivo e profissional.""",
)

print("Agente ARIA-SDR criado com sucesso!")

# Setup our AgentOS app
agent_os = AgentOS(
    description="ARIA-SDR - Agente de Relacionamento Inteligente da AR Online",
    agents=[aria_agent],
)

print("AgentOS configurado com sucesso!")

# Get the FastAPI app
app = agent_os.get_app()

print("FastAPI app obtida com sucesso!")
print("AgentOS pronto para uso!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
