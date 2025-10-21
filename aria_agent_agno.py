"""
ARIA Agent - Versão Completa com Agno Framework
Integra: Web Search, RAG Local, Chat History
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Agno imports
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.db.sqlite import SqliteDb

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_ID = os.getenv("CHAT_MODEL", "gpt-4o-mini")

# ============================================
# ARIA Agent - Configuração Completa
# ============================================

def create_aria_agent(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    use_web_search: bool = True,
    use_knowledge: bool = True,
    use_history: bool = True,
) -> Agent:
    """
    Cria o agente ARIA com todas as funcionalidades do Agno.
    
    Args:
        user_id: ID do usuário para histórico personalizado
        session_id: ID da sessão atual
        use_web_search: Habilitar busca na web
        use_knowledge: Habilitar base de conhecimento local
        use_history: Habilitar histórico de conversas
    
    Returns:
        Agent configurado
    """
    
    # Configurar ferramentas
    tools = []
    if use_web_search:
        tools.append(DuckDuckGoTools())
    
    # Configurar base de conhecimento
    knowledge = None
    if use_knowledge:
        knowledge = Knowledge(
            vector_db=LanceDb(
                uri="tmp/lancedb",
                table_name="aria_knowledge",
                search_type=SearchType.hybrid,  # Busca híbrida (vetorial + texto)
                embedder=OpenAIEmbedder(
                    id="text-embedding-3-small",
                    dimensions=1536
                ),
            ),
        )
    
    # Configurar banco de dados para histórico
    db = None
    if use_history:
        db = SqliteDb(db_file="tmp/aria_agents.db")
    
    # Instruções detalhadas para o agente
    instructions = """
Você é a ARIA (Assistente de Relacionamento Inteligente AR Online).

## Suas Funções Principais:

1. **Classificação de Rotas**
   - Identifique se o usuário quer "envio" ou "recebimento" de mensagens
   - Palavras-chave envio: enviar, mandar, disparar, disparo
   - Palavras-chave recebimento: recebi, recebeu, chegou, abriu, leitura

2. **Análise de Volume**
   - Volume BAIXO: < 1200 mensagens/mês → Ação: comprar créditos
   - Volume ALTO: >= 1200 mensagens/mês → Ação: agendar com time comercial

3. **Respostas com Base de Conhecimento**
   - SEMPRE busque na base de conhecimento primeiro
   - Use search_knowledge=True para perguntas sobre:
     * Como funciona
     * Preços
     * Prazos
     * Recursos do sistema
   - Se não encontrar na base, use web search como fallback

4. **Busca na Web (quando necessário)**
   - Use DuckDuckGo para informações atualizadas
   - Útil para: notícias, eventos recentes, atualizações
   - SEMPRE cite a fonte quando usar web search

5. **Contexto de Conversas**
   - Lembre-se das mensagens anteriores do usuário
   - Seja consistente nas respostas
   - Personalize baseado no histórico

## Estilo de Comunicação:
- Tom: Cordial, objetivo e profissional
- Idioma: Português brasileiro
- Formato: Use markdown quando apropriado
- Emojis: Apenas quando contextual

## Prioridade de Busca:
1. Histórico da conversa (contexto)
2. Base de conhecimento (local)
3. Web search (se necessário)

## IMPORTANTE:
- Sempre identifique números quando mencionado volume
- Seja preciso nas classificações
- Cite fontes quando usar informações externas
- Mantenha LGPD: peça apenas informações necessárias
"""
    
    # Criar agente
    agent = Agent(
        name="ARIA-SDR",
        model=OpenAIChat(
            id=MODEL_ID,
            api_key=OPENAI_API_KEY,
        ),
        tools=tools,
        knowledge=knowledge,
        search_knowledge=use_knowledge,  # CRÍTICO para RAG!
        db=db,
        user_id=user_id or "default",
        session_id=session_id,
        add_history_to_context=use_history,
        num_history_runs=5,  # Últimas 5 interações
        instructions=instructions,
        markdown=True,
        show_tool_calls=False,  # Não mostrar chamadas internas
        debug_mode=False,
    )
    
    return agent


# ============================================
# Singleton - Reutilizar agente (performance)
# ============================================

_agent_cache = {}

def get_aria_agent(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Agent:
    """
    Obtém agente ARIA (reutiliza se já existe).
    
    IMPORTANTE: Nunca criar agentes em loops!
    Sempre reutilizar para melhor performance.
    """
    cache_key = f"{user_id or 'default'}_{session_id or 'default'}"
    
    if cache_key not in _agent_cache:
        _agent_cache[cache_key] = create_aria_agent(
            user_id=user_id,
            session_id=session_id,
        )
    
    return _agent_cache[cache_key]


# ============================================
# Funções Auxiliares
# ============================================

def add_to_knowledge_base(texts: list[str], source: str = "manual"):
    """
    Adiciona textos à base de conhecimento local.
    
    Args:
        texts: Lista de textos para adicionar
        source: Fonte dos textos (para rastreamento)
    """
    agent = create_aria_agent(use_history=False)
    
    if agent.knowledge:
        for text in texts:
            agent.knowledge.load_text(
                text=text,
                metadata={"source": source}
            )
        print(f"[OK] {len(texts)} documento(s) adicionado(s) à base de conhecimento")


def test_agent():
    """Testa o agente ARIA com exemplos."""
    print("\n=== Testando ARIA Agent ===\n")
    
    # Criar agente
    agent = get_aria_agent(user_id="test-user", session_id="test-session")
    
    # Teste 1: Roteamento + Volume
    print("1. Teste: Volume alto")
    response = agent.run("Quero enviar 2000 mensagens para meus clientes")
    print(f"Resposta: {response.content}\n")
    
    # Teste 2: Conhecimento
    print("2. Teste: Base de conhecimento")
    response = agent.run("O que é ARIA?")
    print(f"Resposta: {response.content}\n")
    
    # Teste 3: Web Search (se habilitado)
    print("3. Teste: Web search")
    response = agent.run("Quais são as últimas notícias sobre WhatsApp Business API?")
    print(f"Resposta: {response.content}\n")
    
    # Teste 4: Histórico
    print("4. Teste: Contexto (deve lembrar da pergunta anterior)")
    response = agent.run("E quanto custa isso?")
    print(f"Resposta: {response.content}\n")
    
    print("=== Testes Concluídos ===")


if __name__ == "__main__":
    # Exemplo de uso
    print("ARIA Agent - Versão Completa")
    print("-" * 50)
    
    # Adicionar conhecimento inicial
    print("\n[*] Adicionando conhecimento inicial...")
    knowledge_texts = [
        "ARIA é um sistema de relacionamento inteligente desenvolvido com o framework Agno. Oferece atendimento automatizado via WhatsApp, classificação de volume e roteamento inteligente.",
        "Para volumes acima de 1200 mensagens/mês, recomendamos agendar com nossa equipe comercial. Volumes menores podem comprar créditos diretamente.",
        "A AR Online oferece envio de mensagens via WhatsApp Business API com integração ao Mindchat.",
    ]
    add_to_knowledge_base(knowledge_texts, source="faq")
    
    # Testar agente
    test_agent()

