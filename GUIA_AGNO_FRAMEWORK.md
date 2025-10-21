# 🤖 Guia de Uso do Agno Framework - ARIA-SDR

Este guia explica como o framework Agno é utilizado no projeto ARIA-SDR e como trabalhar com ele de forma eficiente.

---

## 📚 Índice

1. [O que é Agno?](#o-que-é-agno)
2. [Arquitetura no ARIA-SDR](#arquitetura-no-aria-sdr)
3. [Uso Correto do Agno](#uso-correto-do-agno)
4. [Padrões Implementados](#padrões-implementados)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Erros Comuns](#erros-comuns)
7. [Otimizações](#otimizações)

---

## 🎯 O que é Agno?

**Agno** é um framework Python para construir sistemas de IA agentic. Ele fornece:

- 🤖 **Agentes** - Entidades autônomas com modelos de IA
- 🔧 **Tools** - Ferramentas que agentes podem usar
- 💾 **Knowledge** - Bases de conhecimento com RAG
- 🔄 **Workflows** - Orquestração de agentes
- 👥 **Teams** - Múltiplos agentes trabalhando juntos

**Versão no projeto**: Agno 2.1.0

---

## 🏗️ Arquitetura no ARIA-SDR

### Estrutura de Arquivos

```
aria-platform/
├── main.py                          # FastAPI + Endpoints
├── agno/
│   ├── aria_agent_optimized.py     # ⭐ Agente ARIA otimizado
│   ├── agentos_config.yaml         # Configuração AgentOS
│   └── agentos_config_optimized.yaml
└── agent_with_user_memory.py       # Exemplo com memória
```

### Fluxo de Dados

```
FastAPI Request
      ↓
classify_route() (Regras determinísticas)
      ↓
want_rag() (Heurística)
      ↓
fetch_rag_context() (RAG via Supabase)
      ↓
OpenAI Chat Completions (GPT-4o-mini)
      ↓
Response com thread_id e variáveis
```

---

## ✅ Uso Correto do Agno

### ❌ ERRADO: Criar Agente em Loop

```python
# NUNCA FAÇA ISSO - Performance terrível
for mensagem in mensagens:
    agent = Agent(model=OpenAIChat(id="gpt-4o-mini"))  # ❌
    response = agent.run(mensagem)
```

**Problema**: Cria novo agente a cada iteração, causando overhead massivo.

### ✅ CORRETO: Reutilizar Agente

```python
# SEMPRE FAÇA ASSIM - Performance otimizada
agent = Agent(model=OpenAIChat(id="gpt-4o-mini"))  # ✅ Criar UMA vez

for mensagem in mensagens:
    response = agent.run(mensagem)  # ✅ Reutilizar
```

**Benefício**: ~80% mais rápido, menos uso de memória.

---

## 🎨 Padrões Implementados

### 1. Singleton Pattern para Agente

**Arquivo**: `agno/aria_agent_optimized.py`

```python
# Instância global do agente (REUTILIZAÇÃO)
_aria_agent = None

def get_aria_agent():
    """Retorna a instância do agente ARIA (singleton pattern)"""
    global _aria_agent
    if _aria_agent is None:
        _aria_agent = create_aria_agent()
    return _aria_agent

# USO:
agent = get_aria_agent()  # Sempre retorna a mesma instância
```

### 2. Agent com Knowledge (RAG)

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.embedder.openai import OpenAIEmbedder

knowledge = Knowledge(
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="aria_knowledge",
        search_type=SearchType.hybrid,  # FTS + Vector
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    knowledge=knowledge,
    search_knowledge=True,  # ⚠️ CRÍTICO para RAG agentic
    instructions="Use a base de conhecimento para responder",
)
```

### 3. Agent com Histórico

```python
from agno.db.sqlite import SqliteDb

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    db=SqliteDb(db_file="tmp/aria_agents.db"),
    user_id="user-123",
    add_history_to_context=True,  # Adiciona mensagens anteriores
    num_history_runs=3,            # Últimas 3 conversas
)
```

### 4. Agent com Output Schema (Estruturado)

```python
from pydantic import BaseModel

class ARIAResponse(BaseModel):
    thread_id: str
    reply_text: str
    routing_action: str
    confidence_score: float

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    output_schema=ARIAResponse,  # Resposta estruturada
)

# Response é validada automaticamente
result: ARIAResponse = agent.run(query).content
print(result.routing_action)  # Type-safe
```

---

## 💡 Exemplos Práticos

### Exemplo 1: Agente Simples

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions="Você é a ARIA, assistente da AR Online",
    markdown=True,
)

response = agent.print_response("Como funciona o envio de mensagens?", stream=True)
```

### Exemplo 2: Agente com Tools

```python
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    instructions="Pesquise informações na web quando necessário",
    show_tool_calls=True,  # Debug: mostrar chamadas de tools
)

response = agent.run("Qual o preço atual do Bitcoin?")
```

### Exemplo 3: Agente Async

```python
import asyncio

async def processar_mensagens():
    agent = get_aria_agent()
    
    mensagens = [
        "Preciso enviar 1500 emails",
        "Quanto custa?",
        "Como faço para começar?"
    ]
    
    for msg in mensagens:
        response = await agent.arun(msg)  # Async
        print(f"Resposta: {response.content}")

asyncio.run(processar_mensagens())
```

### Exemplo 4: Workflow (Fluxo Programático)

```python
from agno.workflow.workflow import Workflow
from agno.db.sqlite import SqliteDb

async def processar_lead(session_state, mensagem: str):
    # Etapa 1: Classificar volume
    classificacao = await classificador.arun(mensagem)
    
    # Etapa 2: Roteamento baseado em classificação
    if classificacao.content.volume == "alto":
        resultado = await agendador.arun(mensagem)
    else:
        resultado = await vendedor.arun(mensagem)
    
    return resultado

workflow = Workflow(
    name="Processamento de Lead",
    steps=processar_lead,
    db=SqliteDb(db_file="tmp/workflow.db"),
)

# Executar
resultado = workflow.run(mensagem="Preciso enviar 2000 mensagens")
```

---

## ⚠️ Erros Comuns

### Erro 1: Esquecer `search_knowledge=True`

```python
# ❌ ERRADO - Knowledge não será usada
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    knowledge=knowledge,
    # search_knowledge=True,  # ← FALTANDO!
)

# ✅ CORRETO
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    knowledge=knowledge,
    search_knowledge=True,  # ✅ Agora funciona
)
```

### Erro 2: Usar SQLite em Produção

```python
# ❌ ERRADO - SQLite não é para produção
from agno.db.sqlite import SqliteDb

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    db=SqliteDb(db_file="tmp/agents.db"),  # ❌ Produção
)

# ✅ CORRETO - PostgreSQL em produção
from agno.db.postgres import PostgresDb

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    db=PostgresDb(db_url=os.getenv("DATABASE_URL")),  # ✅
)
```

### Erro 3: Não Adicionar Histórico quando Necessário

```python
# ❌ ERRADO - Agente não lembra contexto
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    db=SqliteDb(db_file="tmp/agents.db"),
    # add_history_to_context=True,  # ← FALTANDO!
)

# ✅ CORRETO - Agente lembra conversas anteriores
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    db=SqliteDb(db_file="tmp/agents.db"),
    add_history_to_context=True,  # ✅
    num_history_runs=3,
)
```

### Erro 4: Usar Team quando Single Agent Resolve

```python
# ❌ COMPLEXO DEMAIS - Team desnecessário
from agno.team.team import Team

pesquisador = Agent(...)
escritor = Agent(...)

team = Team(
    members=[pesquisador, escritor],
    model=OpenAIChat(id="gpt-4o"),
)

# ✅ MAIS SIMPLES - Um agente com tools
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    instructions="Pesquise e escreva artigos",
)
```

---

## 🚀 Otimizações

### 1. Cache de Embeddings

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embedding(text: str) -> list[float]:
    """Cache embeddings para evitar chamadas repetidas"""
    client = OpenAI(api_key=OPENAI_API_KEY)
    return client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding
```

### 2. Batch Processing

```python
# ❌ LENTO - Uma por vez
for msg in mensagens:
    embedding = get_embedding(msg)

# ✅ RÁPIDO - Batch
embeddings = client.embeddings.create(
    model="text-embedding-3-small",
    input=mensagens  # Lista de mensagens
).data
```

### 3. Configuração para Produção

```python
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    show_tool_calls=False,    # ✅ Não mostrar em prod
    debug_mode=False,          # ✅ Desabilitar debug
    markdown=True,             # ✅ Formatação
)
```

### 4. Timeout e Retry

```python
from openai import OpenAI

client = OpenAI(
    api_key=OPENAI_API_KEY,
    timeout=30.0,           # Timeout de 30s
    max_retries=3,          # 3 tentativas
)
```

---

## 📊 Quando Usar Cada Padrão

### Single Agent (90% dos casos)

✅ Use quando:
- Uma tarefa ou domínio claro
- Pode ser resolvido com tools + instruções
- Exemplo: FAQ, classificação, busca

```python
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    instructions="...",
)
```

### Team (Coordenação Autônoma)

✅ Use quando:
- Múltiplos especialistas diferentes
- Agentes decidem quem faz o quê via LLM
- Tarefas complexas com múltiplas perspectivas
- Exemplo: Pesquisa + Análise + Escrita

```python
team = Team(
    members=[pesquisador, analista, escritor],
    model=OpenAIChat(id="gpt-4o"),
)
```

### Workflow (Controle Programático)

✅ Use quando:
- Passos sequenciais com fluxo claro
- Precisa de lógica condicional ou branching
- Controle total sobre ordem de execução
- Exemplo: ETL, pipelines, automações

```python
workflow = Workflow(
    name="Pipeline",
    steps=funcao_com_logica,
    db=SqliteDb(db_file="tmp/workflow.db"),
)
```

---

## 🔧 Configuração no ARIA-SDR

### Estrutura Atual

O ARIA-SDR usa **abordagem híbrida**:

1. **FastAPI** - Endpoints e lógica de negócio
2. **Regras Determinísticas** - Classificação rápida
3. **RAG Manual** - Supabase + OpenAI embeddings
4. **Chat Completions** - OpenAI direto (sem Agno Agents)

### Por que não usa Agno Agents no main.py?

O código atual em `main.py` **não usa** `Agent` do Agno diretamente porque:

1. **Performance** - Chamadas diretas à OpenAI API são mais rápidas
2. **Controle** - Lógica de negócio determinística é prioritária
3. **Simplicidade** - Menos camadas de abstração

### Onde o Agno é Usado?

- **Arquivo**: `agno/aria_agent_optimized.py`
- **Propósito**: Exemplo de implementação otimizada
- **Uso**: Pode ser integrado futuramente

### Como Integrar Agno Agents?

Se quiser usar Agno no `main.py`:

```python
# No início do arquivo
from agno.aria_agent_optimized import get_aria_agent

# No endpoint assist_routing
@app.post("/assist/routing")
def assist_routing(payload: dict, _tok: str = Depends(require_auth)):
    agent = get_aria_agent()
    
    # Usar agente em vez de chat completions
    response = agent.run(user_text)
    
    return {
        "reply_text": response.content.reply_text,
        "thread_id": response.content.thread_id,
        # ...
    }
```

---

## 📖 Recursos Adicionais

### Documentação Oficial

- **Site**: https://docs.agno.com
- **GitHub**: https://github.com/agno-agi/agno
- **Cookbook**: Exemplos em `agno-official/cookbook/`

### Arquivos de Referência no Projeto

1. `agno/aria_agent_optimized.py` - Implementação otimizada
2. `agno/agentos_config.yaml` - Configuração AgentOS
3. `agent_with_user_memory.py` - Exemplo com memória
4. `.cursorrules` - Regras e padrões do Agno

### Exemplos no Projeto

```bash
# Ver exemplos oficiais
cd agno-official/cookbook/

# Agentes básicos
ls agents/

# Workflows
ls workflows/

# Teams
ls teams/
```

---

## ✅ Checklist de Uso Correto

- [ ] Criar agente **uma vez**, reutilizar sempre
- [ ] Usar `search_knowledge=True` quando tiver knowledge base
- [ ] PostgreSQL em produção, SQLite apenas em dev
- [ ] Adicionar histórico quando contexto importa
- [ ] Usar `output_schema` para respostas estruturadas
- [ ] `show_tool_calls=False` e `debug_mode=False` em produção
- [ ] Try-except em torno de `agent.run()`
- [ ] Escolher padrão certo: Single Agent > Workflow > Team

---

## 🎯 Resumo

### Regra de Ouro

> **"Create once, reuse always"** - Crie agentes uma vez e reutilize

### Padrão Recomendado

```python
# 1. Criar agente (singleton)
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = Agent(
            model=OpenAIChat(id="gpt-4o-mini"),
            db=get_database(),
            knowledge=get_knowledge(),
            search_knowledge=True,
            add_history_to_context=True,
            output_schema=ResponseSchema,
        )
    return _agent

# 2. Usar em produção
async def processar(mensagem: str):
    try:
        agent = get_agent()
        response = await agent.arun(mensagem)
        return response.content
    except Exception as e:
        logger.error(f"Erro: {e}")
        return fallback_response()
```

---

**Documentação criada para ARIA-SDR**  
**Framework**: Agno 2.1.0  
**Data**: Outubro 2025

