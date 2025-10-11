# Tutoriais - Agno AgentOS

## 🎯 Guias Passo a Passo

### 📚 **Tutorial 1: Criando Seu Primeiro Agente**

#### Objetivo
Criar um agente básico que responde perguntas sobre um tópico específico.

#### Pré-requisitos
- Python 3.8+ instalado
- Conta no Agno (gratuita)
- Chave de API configurada

#### Passo 1: Instalação
```bash
# Instalar Agno
pip install agno

# Configurar autenticação
ag setup
```

#### Passo 2: Código Básico
```python
from agno import Agent

# Criar agente simples
agent = Agent(
    name="MeuPrimeiroAgente",
    instructions="Você é um assistente útil que responde perguntas sobre tecnologia."
)

# Testar o agente
response = agent.run("O que é inteligência artificial?")
print(response)
```

#### Passo 3: Adicionar Ferramentas
```python
from agno import Agent, Tool

# Ferramenta personalizada
def calcular_idade(ano_nascimento: int) -> str:
    idade = 2025 - ano_nascimento
    return f"Você tem {idade} anos"

# Criar ferramenta
tool = Tool(
    name="calcular_idade",
    description="Calcula a idade baseada no ano de nascimento",
    function=calcular_idade
)

# Agente com ferramenta
agent = Agent(
    name="AgenteComCalculadora",
    instructions="Você pode calcular idades quando necessário.",
    tools=[tool]
)

# Testar
response = agent.run("Quantos anos eu tenho se nasci em 1990?")
print(response)
```

#### Passo 4: Testar no Playground
1. Acesse [app.agno.com](https://app.agno.com)
2. Crie um novo agente
3. Configure as instruções e ferramentas
4. Teste interativamente

---

### 🔍 **Tutorial 2: Agente com Busca na Web**

#### Objetivo
Criar um agente que pode buscar informações atualizadas na internet.

#### Passo 1: Configuração
```python
from agno import Agent, Tool
import requests

# Ferramenta de busca web
def buscar_web(query: str) -> str:
    """Busca informações na web"""
    try:
        # Simulação de busca (substitua por API real)
        return f"Resultados da busca por: {query}"
    except Exception as e:
        return f"Erro na busca: {e}"

# Criar ferramenta
web_search = Tool(
    name="buscar_web",
    description="Busca informações atualizadas na internet",
    function=buscar_web
)
```

#### Passo 2: Agente com Busca
```python
# Agente com capacidade de busca
agent = Agent(
    name="AgentePesquisador",
    instructions="""
    Você é um assistente que pode buscar informações atualizadas na web.
    Use a ferramenta de busca quando precisar de informações recentes.
    Sempre cite suas fontes quando possível.
    """,
    tools=[web_search]
)

# Testar
response = agent.run("Qual é a notícia mais recente sobre IA?")
print(response)
```

#### Passo 3: Integração com API Real
```python
import requests
from agno import Agent, Tool

def buscar_noticias(query: str) -> str:
    """Busca notícias usando NewsAPI"""
    api_key = "SUA_API_KEY_AQUI"
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data["status"] == "ok":
            articles = data["articles"][:3]  # Primeiras 3 notícias
            result = "Notícias encontradas:\n\n"
            for article in articles:
                result += f"📰 {article['title']}\n"
                result += f"🔗 {article['url']}\n\n"
            return result
        else:
            return "Erro ao buscar notícias"
    except Exception as e:
        return f"Erro: {e}"

# Ferramenta de notícias
news_tool = Tool(
    name="buscar_noticias",
    description="Busca notícias recentes sobre um tópico",
    function=buscar_noticias
)

# Agente de notícias
news_agent = Agent(
    name="AgenteNoticias",
    instructions="Você é um assistente de notícias. Busque informações atualizadas quando solicitado.",
    tools=[news_tool]
)
```

---

### 🧠 **Tutorial 3: Agente com Memória**

#### Objetivo
Criar um agente que lembra conversas anteriores.

#### Passo 1: Configuração de Memória
```python
from agno import Agent, Memory

# Configurar memória persistente
memory = Memory(
    storage="sqlite://memoria.db",  # Banco SQLite local
    max_tokens=4000,  # Limite de tokens
    cleanup_interval=300  # Limpeza a cada 5 minutos
)

# Agente com memória
agent = Agent(
    name="AgenteComMemoria",
    instructions="Você é um assistente que lembra conversas anteriores.",
    memory=memory
)
```

#### Passo 2: Teste de Memória
```python
# Primeira conversa
response1 = agent.run("Meu nome é João e eu trabalho com desenvolvimento de software.")
print("Resposta 1:", response1)

# Segunda conversa (deve lembrar)
response2 = agent.run("Qual é o meu nome e o que eu faço?")
print("Resposta 2:", response2)
```

#### Passo 3: Gerenciamento de Memória
```python
# Verificar memória
print("Memória atual:", agent.memory.get_context())

# Limpar memória específica
agent.memory.clear_session("session_id")

# Limpar toda memória
agent.memory.clear_all()
```

---

### 🔗 **Tutorial 4: Integração com Banco de Dados**

#### Objetivo
Criar um agente que consulta e atualiza um banco de dados.

#### Passo 1: Configuração do Banco
```python
import sqlite3
from agno import Agent, Tool

# Criar banco de dados
def criar_banco():
    conn = sqlite3.connect("empresa.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            cargo TEXT,
            salario REAL
        )
    """)
    
    # Inserir dados de exemplo
    funcionarios = [
        ("João Silva", "Desenvolvedor", 5000),
        ("Maria Santos", "Designer", 4000),
        ("Pedro Costa", "Gerente", 8000)
    ]
    
    cursor.executemany(
        "INSERT INTO funcionarios (nome, cargo, salario) VALUES (?, ?, ?)",
        funcionarios
    )
    
    conn.commit()
    conn.close()

criar_banco()
```

#### Passo 2: Ferramentas de Banco
```python
import sqlite3

def consultar_funcionarios(query: str) -> str:
    """Consulta funcionários no banco de dados"""
    conn = sqlite3.connect("empresa.db")
    cursor = conn.cursor()
    
    try:
        if "todos" in query.lower():
            cursor.execute("SELECT * FROM funcionarios")
        elif "desenvolvedor" in query.lower():
            cursor.execute("SELECT * FROM funcionarios WHERE cargo = 'Desenvolvedor'")
        else:
            cursor.execute("SELECT * FROM funcionarios WHERE nome LIKE ?", (f"%{query}%",))
        
        resultados = cursor.fetchall()
        
        if resultados:
            response = "Funcionários encontrados:\n\n"
            for func in resultados:
                response += f"ID: {func[0]}\n"
                response += f"Nome: {func[1]}\n"
                response += f"Cargo: {func[2]}\n"
                response += f"Salário: R$ {func[3]:.2f}\n\n"
            return response
        else:
            return "Nenhum funcionário encontrado."
    
    except Exception as e:
        return f"Erro na consulta: {e}"
    finally:
        conn.close()

def adicionar_funcionario(nome: str, cargo: str, salario: float) -> str:
    """Adiciona novo funcionário"""
    conn = sqlite3.connect("empresa.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO funcionarios (nome, cargo, salario) VALUES (?, ?, ?)",
            (nome, cargo, salario)
        )
        conn.commit()
        return f"Funcionário {nome} adicionado com sucesso!"
    except Exception as e:
        return f"Erro ao adicionar funcionário: {e}"
    finally:
        conn.close()

# Criar ferramentas
consulta_tool = Tool(
    name="consultar_funcionarios",
    description="Consulta funcionários no banco de dados",
    function=consultar_funcionarios
)

adicionar_tool = Tool(
    name="adicionar_funcionario",
    description="Adiciona novo funcionário ao banco",
    function=adicionar_funcionario
)
```

#### Passo 3: Agente de RH
```python
# Agente de Recursos Humanos
rh_agent = Agent(
    name="AgenteRH",
    instructions="""
    Você é um assistente de Recursos Humanos.
    Você pode consultar informações sobre funcionários e adicionar novos funcionários.
    Sempre seja profissional e respeitoso.
    """,
    tools=[consulta_tool, adicionar_tool]
)

# Testar consulta
response = rh_agent.run("Mostre-me todos os funcionários")
print(response)

# Testar adição
response = rh_agent.run("Adicione um novo funcionário chamado Ana Lima, cargo Analista, salário 4500")
print(response)
```

---

### 🌐 **Tutorial 5: Webhook e API REST**

#### Objetivo
Criar uma API REST com webhook para integração externa.

#### Passo 1: API FastAPI
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agno import Agent
import uvicorn

app = FastAPI(title="Agno API")

# Modelo de dados
class MessageRequest(BaseModel):
    message: str
    user_id: str = "default"

class MessageResponse(BaseModel):
    response: str
    user_id: str
    timestamp: str

# Agente global
agent = Agent(
    name="API_Agent",
    instructions="Você é um assistente via API. Seja útil e conciso."
)

@app.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    """Endpoint principal de chat"""
    try:
        response = agent.run(request.message)
        return MessageResponse(
            response=response,
            user_id=request.user_id,
            timestamp=str(datetime.now())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook")
async def webhook(data: dict):
    """Webhook para integrações externas"""
    try:
        message = data.get("message", "")
        response = agent.run(message)
        
        return {
            "status": "success",
            "response": response,
            "webhook_id": data.get("id", "unknown")
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "agent": "online"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Passo 2: Teste da API
```python
import requests
import json

# Teste do endpoint de chat
def test_chat():
    url = "http://localhost:8000/chat"
    data = {
        "message": "Olá, como você está?",
        "user_id": "test_user"
    }
    
    response = requests.post(url, json=data)
    print("Status:", response.status_code)
    print("Resposta:", response.json())

# Teste do webhook
def test_webhook():
    url = "http://localhost:8000/webhook"
    data = {
        "message": "Teste de webhook",
        "id": "webhook_001"
    }
    
    response = requests.post(url, json=data)
    print("Webhook Status:", response.status_code)
    print("Webhook Response:", response.json())

# Executar testes
test_chat()
test_webhook()
```

#### Passo 3: Integração com Sistema Externo
```python
# Exemplo de integração com Slack
import requests

def enviar_para_slack(message: str, webhook_url: str):
    """Envia mensagem para Slack via webhook"""
    payload = {
        "text": message,
        "username": "Agno Bot",
        "icon_emoji": ":robot_face:"
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200

# Usar em produção
def processar_mensagem_slack(slack_message: str):
    # Processar com Agno
    response = agent.run(slack_message)
    
    # Enviar resposta para Slack
    webhook_url = "https://hooks.slack.com/services/SEU/WEBHOOK/URL"
    enviar_para_slack(response, webhook_url)
```

---

### 🎨 **Tutorial 6: Agente Multimodal**

#### Objetivo
Criar um agente que processa texto, imagem e áudio.

#### Passo 1: Configuração Multimodal
```python
from agno import Agent, Tool
import base64
import requests

def analisar_imagem(image_data: str) -> str:
    """Analisa uma imagem"""
    try:
        # Simulação de análise de imagem
        return "Imagem analisada: contém texto e elementos gráficos"
    except Exception as e:
        return f"Erro ao analisar imagem: {e}"

def transcrever_audio(audio_data: str) -> str:
    """Transcreve áudio para texto"""
    try:
        # Simulação de transcrição
        return "Áudio transcrito: 'Olá, este é um teste de áudio'"
    except Exception as e:
        return f"Erro ao transcrever áudio: {e}"

# Ferramentas multimodais
image_tool = Tool(
    name="analisar_imagem",
    description="Analisa imagens e extrai informações",
    function=analisar_imagem
)

audio_tool = Tool(
    name="transcrever_audio",
    description="Transcreve áudio para texto",
    function=transcrever_audio
)
```

#### Passo 2: Agente Multimodal
```python
# Agente multimodal
multimodal_agent = Agent(
    name="AgenteMultimodal",
    instructions="""
    Você é um assistente multimodal que pode:
    - Processar texto
    - Analisar imagens
    - Transcrever áudio
    
    Use as ferramentas apropriadas baseado no tipo de entrada.
    """,
    tools=[image_tool, audio_tool]
)

# Teste com diferentes tipos de entrada
def testar_multimodal():
    # Teste de texto
    response_texto = multimodal_agent.run("Descreva uma imagem de um gato")
    print("Resposta texto:", response_texto)
    
    # Teste de imagem (simulado)
    response_imagem = multimodal_agent.run("Analise esta imagem: [dados_da_imagem]")
    print("Resposta imagem:", response_imagem)
    
    # Teste de áudio (simulado)
    response_audio = multimodal_agent.run("Transcreva este áudio: [dados_do_audio]")
    print("Resposta áudio:", response_audio)
```

---

### 🚀 **Tutorial 7: Deploy em Produção**

#### Objetivo
Fazer deploy do agente em ambiente de produção.

#### Passo 1: Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Passo 2: Docker Compose
```yaml
version: '3.8'

services:
  agno-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AGNO_API_KEY=${AGNO_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - agno-api
    restart: unless-stopped
```

#### Passo 3: Configuração de Produção
```python
# config.py
import os
from agno import Agent

class ProductionConfig:
    # Configurações de produção
    AGNO_API_KEY = os.getenv("AGNO_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Configurações de segurança
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
    
    # Configurações de performance
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
    TIMEOUT = int(os.getenv("TIMEOUT", "30"))

# Agente de produção
def create_production_agent():
    return Agent(
        name="ProductionAgent",
        instructions="Você é um assistente de produção. Seja eficiente e preciso.",
        model="gpt-3.5-turbo",  # Modelo mais rápido para produção
        temperature=0.1,  # Mais determinístico
        max_tokens=1000,  # Limite de tokens
        timeout=30  # Timeout de 30 segundos
    )
```

#### Passo 4: Monitoramento
```python
import logging
from agno import Agent, Metrics

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agno.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('agno')

# Agente com monitoramento
def create_monitored_agent():
    agent = Agent(name="MonitoredAgent")
    
    # Configurar métricas
    metrics = Metrics(agent)
    metrics.start()
    
    # Log de todas as interações
    def log_interaction(message, response):
        logger.info(f"Input: {message}")
        logger.info(f"Output: {response}")
        logger.info(f"Metrics: {metrics.get_summary()}")
    
    return agent, log_interaction
```

---

## 🎯 **Próximos Passos**

Após completar estes tutoriais, você estará pronto para:

1. **Criar agentes complexos** com múltiplas ferramentas
2. **Integrar com sistemas empresariais** existentes
3. **Implementar workflows** avançados
4. **Fazer deploy** em produção
5. **Monitorar e otimizar** performance

## 📚 **Recursos Adicionais**

- **Documentação**: [docs.agno.com](https://docs.agno.com)
- **Exemplos**: [github.com/agno-agi/examples](https://github.com/agno-agi/examples)
- **Comunidade**: [community.agno.com](https://community.agno.com)
- **Suporte**: Para dúvidas e problemas

**Última atualização**: Outubro 2025
