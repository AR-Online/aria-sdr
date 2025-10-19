# test_agno_config.py - Teste simples da configuraÃ§Ã£o AgentOS
from agno.os import AgentOS
from agno.os.config import (
    AgentOSConfig,
    ChatConfig,
    DatabaseConfig,
    MemoryConfig,
    MemoryDomainConfig,
)
from agno.agent import Agent
from agno.db.sqlite import SqliteDb

print("Criando databases...")
aria_db = SqliteDb(db_file="tmp/aria_memories.db")
support_db = SqliteDb(db_file="tmp/support_memories.db")

print("Criando agente ARIA...")
aria_agent = Agent(
    name="ARIA-SDR",
    db=aria_db,
    instructions="VocÃª Ã© a ARIA, Agente de Relacionamento Inteligente da AR Online.",
)

print("Configurando AgentOS...")
agent_os = AgentOS(
    description="ARIA-SDR - Agente de Relacionamento Inteligente da AR Online",
    agents=[aria_agent],
    config=AgentOSConfig(
        chat=ChatConfig(
            quick_prompts={
                "aria-sdr": [
                    "O que vocÃª pode fazer?",
                    "Como funciona a AR Online?",
                    "Quero enviar e-mails em massa",
                ]
            }
        ),
        memory=MemoryConfig(
            dbs=[
                DatabaseConfig(
                    db_id=aria_db.id,
                    domain_config=MemoryDomainConfig(
                        display_name="ARIA-SDR User Memories",
                    ),
                ),
                DatabaseConfig(
                    db_id=support_db.id,
                    domain_config=MemoryDomainConfig(
                        display_name="Support Flow User Memories",
                    ),
                )
            ],
        ),
    ),
)

print("AgentOS configurado com sucesso!")
print(f"Total de rotas: {len(agent_os.get_routes())}")
print("ConfiguraÃ§Ã£o concluÃ­da!")
