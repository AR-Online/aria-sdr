# Troubleshooting - Agno AgentOS

## 🛠️ Guia de Resolução de Problemas

### 🚨 **Problemas Críticos**

#### Erro: "Agent not responding"
**Sintomas:**
- Agente não responde a comandos
- Timeout em requisições
- Erro 500 no servidor

**Possíveis Causas:**
1. Modelo de IA indisponível
2. Configuração incorreta de ferramentas
3. Problemas de memória
4. Erro na lógica do agente

**Soluções:**
```python
# 1. Verificar status do modelo
from agno import Agent
agent = Agent(name="test")
print(agent.model_status())

# 2. Testar com configuração mínima
simple_agent = Agent(
    name="simple",
    instructions="Responda apenas 'OK'",
    tools=[]
)

# 3. Verificar logs
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Erro: "Authentication failed"
**Sintomas:**
- Erro 401 em todas as requisições
- "Invalid API key" nos logs
- Falha na configuração inicial

**Soluções:**
```bash
# 1. Reconfigurar autenticação
ag setup

# 2. Verificar variável de ambiente
echo $AGNO_API_KEY

# 3. Gerar nova chave
# Acesse: app.agno.com/settings
```

#### Erro: "Memory overflow"
**Sintomas:**
- Agente fica lento com o tempo
- Erro "Out of memory"
- Respostas inconsistentes

**Soluções:**
```python
# 1. Limpar cache
agent.clear_cache()

# 2. Configurar limites de memória
from agno import Agent, Memory
memory = Memory(
    max_tokens=4000,
    cleanup_interval=300  # 5 minutos
)
agent = Agent(memory=memory)

# 3. Usar streaming para respostas longas
response = agent.run_stream("pergunta longa")
```

### ⚠️ **Problemas de Performance**

#### Agente muito lento
**Diagnóstico:**
```python
import time
from agno import Agent

agent = Agent(name="perf_test")

# Medir tempo de resposta
start = time.time()
response = agent.run("teste")
end = time.time()

print(f"Tempo de resposta: {end - start:.2f}s")
```

**Otimizações:**
1. **Usar modelo mais rápido**:
```python
agent = Agent(
    name="fast_agent",
    model="gpt-3.5-turbo"  # Mais rápido que gpt-4
)
```

2. **Implementar cache**:
```python
from agno import Agent, Cache

cache = Cache(ttl=3600)  # 1 hora
agent = Agent(cache=cache)
```

3. **Reduzir contexto**:
```python
agent = Agent(
    name="minimal",
    max_context_length=2000  # Limitar contexto
)
```

#### Alto uso de memória
**Monitoramento:**
```python
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Uso de memória: {memory_mb:.2f} MB")

# Usar antes e depois de operações
monitor_memory()
response = agent.run("pergunta")
monitor_memory()
```

**Soluções:**
1. **Garbage collection**:
```python
import gc
gc.collect()
```

2. **Limitar número de agentes**:
```python
# Não criar muitos agentes simultaneamente
MAX_AGENTS = 10
```

3. **Usar agentes stateless**:
```python
agent = Agent(
    name="stateless",
    memory=None  # Sem memória persistente
)
```

### 🔗 **Problemas de Integração**

#### Webhook não funciona
**Teste básico:**
```python
from fastapi import FastAPI
from agno import Agent
import uvicorn

app = FastAPI()
agent = Agent(name="webhook_test")

@app.post("/webhook")
async def webhook(data: dict):
    try:
        response = agent.run(data["message"])
        return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Testar localmente
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Verificações:**
1. **URL correta**: Confirme se a URL está acessível
2. **Headers**: Verifique Content-Type e Authorization
3. **Payload**: Confirme formato do JSON
4. **Logs**: Ative logs para debug

#### Integração com banco de dados falha
**Teste de conectividade:**
```python
import sqlite3
import psycopg2
from agno import Agent, Knowledge

# Teste SQLite
try:
    conn = sqlite3.connect("test.db")
    print("SQLite: OK")
except Exception as e:
    print(f"SQLite Error: {e}")

# Teste PostgreSQL
try:
    conn = psycopg2.connect(
        host="localhost",
        database="test",
        user="user",
        password="pass"
    )
    print("PostgreSQL: OK")
except Exception as e:
    print(f"PostgreSQL Error: {e}")
```

**Soluções:**
1. **Verificar credenciais**
2. **Testar conectividade de rede**
3. **Usar connection pooling**
4. **Implementar retry logic**

#### API externa não responde
**Teste de conectividade:**
```python
import requests
from agno import Agent, CustomApiTool

# Teste básico
try:
    response = requests.get("https://api.exemplo.com/health", timeout=5)
    print(f"API Status: {response.status_code}")
except Exception as e:
    print(f"API Error: {e}")

# Teste com CustomApiTool
api_tool = CustomApiTool(
    name="test_api",
    base_url="https://api.exemplo.com",
    timeout=10,
    retries=3
)
```

**Soluções:**
1. **Implementar timeout**
2. **Adicionar retry logic**
3. **Usar circuit breaker**
4. **Implementar fallback**

### 🧠 **Problemas de IA**

#### Respostas inconsistentes
**Diagnóstico:**
```python
# Testar com mesma pergunta múltiplas vezes
questions = [
    "Qual é a capital do Brasil?",
    "Qual é a capital do Brasil?",
    "Qual é a capital do Brasil?"
]

for i, question in enumerate(questions):
    response = agent.run(question)
    print(f"Resposta {i+1}: {response}")
```

**Soluções:**
1. **Usar temperatura baixa**:
```python
agent = Agent(
    name="consistent",
    temperature=0.1  # Mais determinístico
)
```

2. **Adicionar instruções específicas**:
```python
agent = Agent(
    name="specific",
    instructions="Sempre responda de forma consistente e precisa"
)
```

3. **Usar few-shot examples**:
```python
agent = Agent(
    name="few_shot",
    examples=[
        {"input": "Capital do Brasil?", "output": "Brasília"},
        {"input": "Capital da França?", "output": "Paris"}
    ]
)
```

#### Agente não segue instruções
**Verificação:**
```python
# Testar instruções simples
agent = Agent(
    name="test_instructions",
    instructions="Sempre responda apenas 'SIM' ou 'NÃO'"
)

response = agent.run("Olá, como você está?")
print(f"Resposta: {response}")
# Deveria ser apenas "SIM" ou "NÃO"
```

**Soluções:**
1. **Instruções mais específicas**:
```python
agent = Agent(
    name="specific",
    instructions="""
    Você é um assistente que responde apenas SIM ou NÃO.
    Não forneça explicações adicionais.
    Não faça perguntas de volta.
    """
)
```

2. **Usar system prompt**:
```python
agent = Agent(
    name="system_prompt",
    system_prompt="Você é um assistente direto e objetivo"
)
```

3. **Implementar validação**:
```python
def validate_response(response: str) -> bool:
    return response.upper() in ["SIM", "NÃO"]

response = agent.run("pergunta")
if not validate_response(response):
    print("Resposta inválida!")
```

### 📊 **Problemas de Monitoramento**

#### Métricas não aparecem
**Verificação:**
```python
from agno import Agent, Metrics

agent = Agent(name="metrics_test")

# Ativar métricas
metrics = Metrics(agent)
metrics.start()

# Executar operações
response = agent.run("teste")

# Verificar métricas
print(f"Requisições: {metrics.request_count}")
print(f"Tempo médio: {metrics.avg_response_time}")
```

**Soluções:**
1. **Verificar configuração**:
```python
# Verificar se métricas estão habilitadas
print(agent.metrics_enabled)
```

2. **Usar dashboard**:
```python
# Acessar dashboard
# app.agno.com/dashboard
```

3. **Implementar logging customizado**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('agno')
```

### 🔧 **Ferramentas de Debug**

#### Script de diagnóstico completo
```python
#!/usr/bin/env python3
"""
Script de diagnóstico do Agno AgentOS
"""

import os
import sys
import time
import requests
from agno import Agent

def run_diagnostics():
    print("🔍 Diagnóstico do Agno AgentOS")
    print("=" * 50)
    
    # 1. Verificar instalação
    try:
        import agno
        print(f"✅ Agno instalado: {agno.__version__}")
    except ImportError:
        print("❌ Agno não instalado")
        return
    
    # 2. Verificar autenticação
    api_key = os.getenv('AGNO_API_KEY')
    if api_key:
        print("✅ API Key configurada")
    else:
        print("❌ API Key não encontrada")
    
    # 3. Testar agente básico
    try:
        agent = Agent(name="diagnostic")
        start = time.time()
        response = agent.run("teste")
        end = time.time()
        print(f"✅ Agente funcionando: {end - start:.2f}s")
    except Exception as e:
        print(f"❌ Erro no agente: {e}")
    
    # 4. Testar conectividade
    try:
        response = requests.get("https://api.agno.com/health", timeout=5)
        print(f"✅ API online: {response.status_code}")
    except Exception as e:
        print(f"❌ API offline: {e}")
    
    print("\n🎯 Diagnóstico concluído!")

if __name__ == "__main__":
    run_diagnostics()
```

#### Comandos úteis
```bash
# Verificar versão
ag --version

# Verificar configuração
ag config

# Limpar cache
ag cache clear

# Verificar status
ag status

# Logs em tempo real
ag logs --follow

# Teste de conectividade
ag ping
```

---

## 📞 **Suporte Adicional**

Se os problemas persistirem:

1. **Consulte a documentação**: [docs.agno.com](https://docs.agno.com)
2. **Participe da comunidade**: [community.agno.com](https://community.agno.com)
3. **Abra uma issue**: [GitHub Issues](https://github.com/agno-agi/agno/issues)
4. **Contate o suporte**: Para planos Pro/Enterprise

**Última atualização**: Outubro 2025
