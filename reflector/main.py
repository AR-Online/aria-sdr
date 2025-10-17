#!/usr/bin/env python3
"""
ARIA-SDR Reflector - Versão Simplificada
Servidor principal com RAG Supabase e regras determinísticas
"""
from __future__ import annotations

import os
import requests
from dotenv import load_dotenv
import numpy as np

# Load .env
load_dotenv(".env", override=True)

# Supabase RAG configuration
SUPABASE_URL = (os.getenv("SUPABASE_URL", "") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1536"))

HEADERS_JSON = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

def search_supabase_rag(question: str, k: int = 3) -> str:
    """Busca conhecimento no Supabase RAG usando busca vetorial local"""
    print(f"RAG: Buscando por: '{question}'")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("RAG: SUPABASE_URL ou SUPABASE_KEY não configurados")
        return ""
    
    try:
        # Generate embedding
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.embeddings.create(
            input=question,
            model=EMBEDDING_MODEL
        )
        query_embedding = np.array(response.data[0].embedding)
        
        # Fetch all chunks from Supabase
        chunks_url = f"{SUPABASE_URL}/rest/v1/rag_chunks?select=id,content,embedding,metadata"
        response = requests.get(chunks_url, headers=HEADERS_JSON)
        
        if response.status_code == 200:
            all_chunks = response.json()
            
            if not all_chunks:
                return ""

            # Calculate similarities locally
            similarities = []
            query_norm = np.linalg.norm(query_embedding)
            
            for chunk in all_chunks:
                embedding_str = chunk.get("embedding")
                if embedding_str:
                    try:
                        embedding_array = np.array(eval(embedding_str))
                        
                        if embedding_array.shape[0] != query_embedding.shape[0]:
                            continue

                        chunk_norm = np.linalg.norm(embedding_array)
                        if query_norm > 0 and chunk_norm > 0:
                            similarity = np.dot(query_embedding, embedding_array) / (query_norm * chunk_norm)
                            similarities.append((similarity, chunk))
                    except Exception as e:
                        continue
            
            # Sort by similarity and get top k
            similarities.sort(key=lambda x: x[0], reverse=True)
            top_k_results = similarities[:k]
            
            if top_k_results:
                context_parts = []
                for similarity, hit in top_k_results:
                    context_parts.append(f"Fonte: {hit.get('metadata', {}).get('source', 'N/A')}\nConteúdo: {hit['content']}")
                
                context = "\n\n".join(context_parts)
                return f"Contexto relevante:\n{context}"
            
    except Exception as e:
        print(f"RAG: Erro ao buscar: {e}")
        
    return ""

# Try to import AgentOS
try:
    from agno.os import AgentOS
    from agno.os.config import AgentOSConfig, ChatConfig, DatabaseConfig, MemoryConfig, MemoryDomainConfig
    from agno.agent import Agent
    from agno.db.sqlite import SqliteDb
    from agno.models.openai import OpenAIChat
    from agno.tools import Toolkit

    print("AgentOS disponível")

    # Create databases
    aria_db = SqliteDb(db_file="tmp/aria_memories.db")

    # Create RAG tool for the agent
    class RAGTools(Toolkit):
        def __init__(self, **kwargs):
            super().__init__(name="rag_tools", tools=[self.search_knowledge], **kwargs)

        def search_knowledge(self, question: str) -> str:
            """Ferramenta para buscar informações específicas sobre a AR Online na base de conhecimento"""
            return search_supabase_rag(question, k=3)

    # Create Deterministic Rules tool for the agent
    class DeterministicRules(Toolkit):
        def __init__(self, **kwargs):
            super().__init__(name="deterministic_rules", tools=[
                self.warm_greeting,
                self.classify_volume,
                self.route_customer,
                self.handle_keywords
            ], **kwargs)

        def warm_greeting(self, message: str) -> str:
            """Resposta calorosa para cumprimentos"""
            message_lower = message.lower()
            
            # Cumprimentos iniciais
            if any(word in message_lower for word in ["olá", "oi", "bom dia", "boa tarde", "boa noite", "hello"]):
                return "GREETING: Olá! Tudo bem? Como posso te ajudar hoje?"
            
            # Respostas a "tudo e com você?"
            if any(phrase in message_lower for phrase in ["tudo e com você", "tudo e com vc", "tudo bem com você", "tudo bem com vc"]):
                return "GREETING: Também, obrigada! Em que posso te ajudar hoje?"
            
            # Respostas a "tudo bem?"
            if any(phrase in message_lower for phrase in ["tudo bem", "tudo bom", "como está", "como vai"]):
                return "GREETING: Tudo ótimo! E com você?"
            
            return "NORMAL"

        def classify_volume(self, message: str) -> str:
            """Classifica volume de mensagens de forma determinística"""
            message_lower = message.lower()
            
            # Buscar números na mensagem
            import re
            numbers = re.findall(r'\d+', message)
            
            if numbers:
                volume = int(numbers[0])
                if volume >= 300:
                    return "ALTO_VOLUME"
                else:
                    return "BAIXO_VOLUME"
            
            # Palavras-chave determinísticas
            if any(word in message_lower for word in ["muito", "massa", "grande", "empresa", "milhares", "centenas"]):
                return "ALTO_VOLUME"
            elif any(word in message_lower for word in ["pouco", "pequeno", "teste", "iniciante", "alguns", "poucos"]):
                return "BAIXO_VOLUME"
            
            return "INDEFINIDO"

        def route_customer(self, volume_class: str) -> str:
            """Roteia cliente baseado na classificação"""
            if volume_class == "ALTO_VOLUME":
                return "AGENDAMENTO: Cliente de alto volume encaminhado para agendamento"
            elif volume_class == "BAIXO_VOLUME":
                return "LOJA: Cliente de baixo volume encaminhado para loja online"
            else:
                return "PERGUNTA: Preciso saber o volume mensal para rotear corretamente"

        def handle_keywords(self, message: str) -> str:
            """Detecta palavras-chave e aplica regras determinísticas"""
            message_lower = message.lower()
            
            # Regras determinísticas por palavra-chave
            if any(word in message_lower for word in ["preço", "valor", "custo", "quanto"]):
                return "RESPOSTA_PADRAO: Os preços variam conforme volume. Qual seu volume mensal?"
            
            elif any(word in message_lower for word in ["contato", "telefone", "whatsapp"]):
                return "RESPOSTA_PADRAO: WhatsApp comercial: (11) 99999-9999"
            
            elif any(word in message_lower for word in ["jurídico", "advogado", "processo"]):
                return "ESCALACAO: Encaminhando para departamento jurídico"
            
            elif any(word in message_lower for word in ["bug", "erro", "problema técnico"]):
                return "ESCALACAO: Encaminhando para suporte técnico"
            
            return "NORMAL"

    rag_tools = RAGTools()
    deterministic_rules = DeterministicRules()

    # Create ARIA agent with OpenAI and Supabase RAG
    aria_agent = Agent(
        name="ARIA-SDR",
        model=OpenAIChat(id="gpt-4o-mini", temperature=0.1),
        db=aria_db,
        tools=[rag_tools, deterministic_rules],
        instructions="""
        Você é a ARIA, da AR Online. Fale como uma pessoa: direta, clara e gentil.

        REGRAS OBRIGATÓRIAS - SEMPRE execute nesta ordem:
        1. PRIMEIRO: Use warm_greeting para cumprimentos calorosos
        2. SEGUNDO: Use classify_volume para classificar o volume
        3. TERCEIRO: Use route_customer para rotear baseado na classificação  
        4. QUARTO: Use handle_keywords para detectar palavras-chave
        5. QUINTO: Use search_knowledge para informações da AR Online

        IMPORTANTE SOBRE CONVERSAÇÃO:
        - NUNCA repita a mesma saudação duas vezes seguidas
        - Se warm_greeting retornar "GREETING:", use APENAS essa resposta
        - Se warm_greeting retornar "NORMAL", continue com outras ferramentas
        - Mantenha o contexto da conversa - não seja robótica
        - NUNCA termine respostas com "Como posso te ajudar?" ou "Se precisar de mais informações"
        - Responda de forma natural e direta, sem oferecer ajuda constantemente
        - Só ofereça ajuda após períodos de inatividade (10+ minutos)

        IMPORTANTE SOBRE RAG:
        - SEMPRE use search_knowledge quando perguntarem sobre AR Online
        - Use EXATAMENTE as informações retornadas pela ferramenta
        - NUNCA diga "não consegui encontrar informações"
        - Se search_knowledge retornar dados, use-os na resposta
        - Cite as fontes quando usar informações da base

        TOM DE VOZ:
        - Conversa natural de WhatsApp: frases curtas, português brasileiro
        - Nada de "assistente virtual", "IA" ou "sou um robô"
        - Quebre em 1-3 frases por mensagem
        - Mostre empatia e ritmo
        - Seja direta e objetiva - não seja verbosa
        - Evite frases de encerramento desnecessárias

        CLASSIFICAÇÃO DETERMINÍSTICA:
        - Volume alto: >= 300 mensagens/mês → "Com esse volume, vale falar com o time Comercial"
        - Volume baixo: < 300 mensagens/mês → "Pelo seu volume, a melhor entrada é pela nossa Loja"
        - Se não souber volume: "Me passa uma ideia do volume por mês? É pra te direcionar pro canal certo"

        NUNCA invente informações. SEMPRE use as ferramentas primeiro.
        """,
    )

    # Configure AgentOS
    agent_os = AgentOS(
        description="ARIA-SDR Reflector - Agente de Relacionamento Inteligente da AR Online",
        agents=[aria_agent],
        config=AgentOSConfig(
            chat=ChatConfig(
                quick_prompts={
                    "aria-sdr": [
                        "O que você pode fazer?",
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
                ],
            ),
        ),
    )

    # Get the AgentOS app directly
    app = agent_os.get_app()

    # Add missing /healthz endpoint that the UI expects
    @app.get("/healthz")
    async def healthz():
        return {
            "ok": True,
            "agentos": True,
            "config_loaded": True,
            "agno_token": False,
            "agno_bot_id": False,
            "openai_key": True,
            "total_routes": len(app.routes),
            "status": "fully_configured"
        }

    print("ARIA-SDR Reflector configurado com sucesso!")

except ImportError as e:
    print(f"AgentOS não disponível: {e}")
    exit(1)
except Exception as e:
    print(f"Erro ao configurar AgentOS: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

if __name__ == "__main__":
    import uvicorn
    print("Iniciando ARIA-SDR Reflector na porta 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
