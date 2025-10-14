# ARIA-SDR - Configuracao Otimizada do Agno
# Baseado nas melhores praticas do .cursorrules

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.embedder.openai import OpenAIEmbedder
from pydantic import BaseModel
import os

# Configuracao de Banco de Dados
# SQLite para desenvolvimento, PostgreSQL para producao
def get_database():
    """Retorna o banco de dados apropriado para o ambiente"""
    if os.getenv("ENVIRONMENT") == "production":
        from agno.db.postgres import PostgresDb
        return PostgresDb(db_url=os.getenv("DATABASE_URL"))
    else:
        return SqliteDb(db_file="tmp/aria_agents.db")

# Configuracao de Conhecimento/RAG
def get_knowledge_base():
    """Configura base de conhecimento com RAG"""
    return Knowledge(
        vector_db=LanceDb(
            uri="tmp/lancedb",
            table_name="aria_knowledge",
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
    )

# Schema de Resposta Estruturada
class ARIAResponse(BaseModel):
    """Schema para respostas estruturadas da ARIA"""
    thread_id: str
    reply_text: str
    routing_action: str  # "faq", "schedule", "buy_credits"
    volume_classification: str  # "high", "low"
    confidence_score: float
    variables: dict

# Agente ARIA Principal (CRIAR UMA VEZ, REUTILIZAR)
def create_aria_agent():
    """Cria o agente ARIA principal seguindo as melhores praticas"""
    
    return Agent(
        name="ARIA-SDR",
        model=OpenAIChat(id="gpt-4o-mini"),
        db=get_database(),
        knowledge=get_knowledge_base(),
        search_knowledge=True,  # CRITICO: habilita RAG agentico
        output_schema=ARIAResponse,
        add_history_to_context=True,
        num_history_runs=3,
        user_id="aria-sdr-user",
        instructions="""
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
        
        Sempre seja cordial, objetivo e profissional.
        """,
        markdown=True,
    )

# Instancia global do agente (REUTILIZACAO CRITICA)
_aria_agent = None

def get_aria_agent():
    """Retorna a instancia do agente ARIA (singleton pattern)"""
    global _aria_agent
    if _aria_agent is None:
        _aria_agent = create_aria_agent()
    return _aria_agent

# Funcao de Processamento Otimizada
async def process_aria_message(user_text: str, thread_id: str = None, channel: str = "web"):
    """
    Processa mensagem usando o agente ARIA otimizado
    
    CRITICO: Reutiliza a mesma instancia do agente para performance
    """
    try:
        agent = get_aria_agent()
        
        # Contexto adicional
        context = f"""
        Canal: {channel}
        Thread ID: {thread_id or 'novo'}
        """
        
        # Processar com o agente
        response = await agent.arun(f"{context}\n\nMensagem do usuario: {user_text}")
        
        # Retornar resposta estruturada
        return response.content
        
    except Exception as e:
        # Fallback em caso de erro
        return ARIAResponse(
            thread_id=thread_id or "error_thread",
            reply_text="Desculpe, ocorreu um erro. Tente novamente em alguns instantes.",
            routing_action="faq",
            volume_classification="unknown",
            confidence_score=0.0,
            variables={"error": str(e)}
        )

# Configuracao para Producao
def setup_production_config():
    """Configuracoes especificas para ambiente de producao"""
    return {
        "show_tool_calls": False,
        "debug_mode": False,
        "database": "postgresql",
        "environment": "production"
    }

# Exemplo de uso correto
if __name__ == "__main__":
    import asyncio
    
    async def test_aria():
        # CORRETO: Criar agente uma vez, reutilizar
        agent = get_aria_agent()
        
        # Processar multiplas mensagens
        messages = [
            "Ola, preciso de ajuda",
            "Quero enviar 1500 emails por mes",
            "Como funciona a AR Online?"
        ]
        
        for msg in messages:
            response = await agent.arun(msg)
            print(f"Resposta: {response.content}")
    
    # Executar teste
    asyncio.run(test_aria())
