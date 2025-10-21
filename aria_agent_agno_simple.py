"""
ARIA Agent - Versão Simples com Agno Framework
Integra: Web Search + Chat History + Supabase (RAG já funcionando)
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Agno imports
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.db.sqlite import SqliteDb

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_ID = os.getenv("CHAT_MODEL", "gpt-4o-mini")

# ============================================
# ARIA Agent - Configuração Simples
# ============================================

def create_aria_agent_simple(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    use_web_search: bool = True,
    use_history: bool = True,
) -> Agent:
    """
    Cria o agente ARIA com Agno (versão simples).
    
    - Web Search: DuckDuckGo
    - Chat History: SQLite
    - RAG: Supabase (via endpoint existente)
    """
    
    # Configurar ferramentas
    tools = []
    if use_web_search:
        tools.append(DuckDuckGoTools())
    
    # Configurar banco de dados para histórico
    db = None
    if use_history:
        db = SqliteDb(db_file="tmp/aria_agents.db")
    
    # Instruções para o agente
    instructions = """
Você é a ARIA (Assistente de Relacionamento Inteligente AR Online).

## Suas Funções:

1. **Classificação de Rotas**
   - Envio: enviar, mandar, disparar
   - Recebimento: recebi, recebeu, chegou

2. **Análise de Volume**
   - BAIXO (< 1200/mês): comprar créditos
   - ALTO (>= 1200/mês): agendar com comercial

3. **Busca na Web**
   - Use DuckDuckGo quando precisar de info atualizada
   - SEMPRE cite a fonte

4. **Contexto**
   - Lembre das mensagens anteriores
   - Seja consistente

## Estilo:
- Tom: Cordial e profissional
- Português BR
- Use markdown
- Cite fontes

## IMPORTANTE:
- Identifique números de volume
- Seja preciso
- Respeite LGPD
"""
    
    # Criar agente
    agent = Agent(
        name="ARIA-SDR",
        model=OpenAIChat(
            id=MODEL_ID,
            api_key=OPENAI_API_KEY,
        ),
        tools=tools,
        storage=db,
        user_id=user_id or "default",
        session_id=session_id,
        add_history_to_messages=use_history,
        num_history_responses=5,
        instructions=instructions,
        markdown=True,
    )
    
    return agent


# ============================================
# Cache de agentes (performance)
# ============================================

_agent_cache = {}

def get_aria_agent(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Agent:
    """Obtém agente ARIA (reutiliza se já existe)."""
    cache_key = f"{user_id or 'default'}_{session_id or 'default'}"
    
    if cache_key not in _agent_cache:
        _agent_cache[cache_key] = create_aria_agent_simple(
            user_id=user_id,
            session_id=session_id,
        )
    
    return _agent_cache[cache_key]


def clear_agent_cache():
    """Limpa cache de agentes."""
    global _agent_cache
    _agent_cache = {}


# ============================================
# Teste
# ============================================

if __name__ == "__main__":
    print("ARIA Agent - Versão Simples com Agno")
    print("=" * 50)
    
    # Criar agente
    agent = get_aria_agent(user_id="test-user", session_id="test-001")
    
    print("\n1. Teste: Volume alto")
    response = agent.run("Quero enviar 2000 mensagens")
    print(f"→ {response.content}\n")
    
    print("2. Teste: Pergunta simples")
    response = agent.run("Como posso fazer isso?")
    print(f"→ {response.content}\n")
    
    print("3. Teste: Web search")
    response = agent.run("Quais as últimas novidades sobre WhatsApp API?")
    print(f"→ {response.content}\n")
    
    print("=" * 50)
    print("Testes concluídos!")

