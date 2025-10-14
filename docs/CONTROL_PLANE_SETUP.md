# ARIA-SDR - Conexão com Control Plane

Este guia explica como conectar o ARIA-SDR AgentOS ao Control Plane do Agno seguindo a [documentação oficial](https://docs.agno.com/agent-os/connecting-your-os).

## 🚀 Início Rápido

### 1. Configurar Ambiente

```bash
# Copiar arquivo de configuração
cp config.env.example .env

# Editar variáveis obrigatórias
# OPENAI_API_KEY=sua_chave_aqui
# WHATSAPP_ACCESS_TOKEN=seu_token_aqui (opcional)
```

### 2. Instalar Dependências

```bash
pip install -U agno fastapi uvicorn
```

### 3. Executar Script de Configuração

```bash
python scripts/connect_to_control_plane.py
```

## 📋 Processo de Conexão

### Passo 1: Iniciar AgentOS

```bash
python aria_agentos_optimized.py
```

O servidor será iniciado em `http://localhost:7777`

### Passo 2: Conectar ao Control Plane

1. **Acesse**: https://platform.agno.com
2. **Faça login** na sua conta Agno
3. **Clique no "+"** ao lado de "Add new OS"
4. **Selecione "Local"** para desenvolvimento
5. **Configure**:
   - **Endpoint URL**: `http://localhost:7777`
   - **OS Name**: `ARIA-SDR Development`
   - **Tags**: `development`, `aria-sdr`, `whatsapp`
6. **Clique em "CONNECT"**

## 🔧 Configurações Avançadas

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `HOST` | Host do servidor | `localhost` |
| `PORT` | Porta do servidor | `7777` |
| `MODEL_PROVIDER` | Provedor do modelo | `openai` |
| `MODEL_ID` | ID do modelo | `gpt-4o-mini` |
| `APP_ENV` | Ambiente | `development` |

### Configuração de Produção

Para produção, configure:
```bash
APP_ENV=production
DATABASE_URL=postgresql://user:pass@host:port/db
HOST=0.0.0.0
PORT=7777
```

## 🛡️ Segurança

### Autenticação Bearer Token

Para proteger sua conexão:

1. **Gere chaves de segurança** no Control Plane
2. **Configure autenticação** no servidor
3. **Use HTTPS** em produção

### Variáveis Sensíveis

Nunca commite:
- `OPENAI_API_KEY`
- `WHATSAPP_ACCESS_TOKEN`
- `DATABASE_URL`
- Chaves de segurança

## 🔍 Verificação da Conexão

Após conectar, verifique:

- ✅ **Status**: "Running" no Control Plane
- ✅ **Agentes**: ARIA-SDR aparece na lista
- ✅ **Chat**: Interface de conversa disponível
- ✅ **Memória**: Sessões sendo registradas
- ✅ **Conhecimento**: Base de conhecimento acessível

## 🚨 Solução de Problemas

### Erro de Conexão

```bash
# Verificar se o servidor está rodando
curl http://localhost:7777/health

# Verificar logs
python aria_agentos_optimized.py
```

### Dependências Faltando

```bash
# Reinstalar dependências
pip install -U agno fastapi uvicorn python-dotenv
```

### Variáveis Não Configuradas

```bash
# Verificar configuração
python scripts/connect_to_control_plane.py
```

## 📚 Recursos Adicionais

- [Documentação AgentOS](https://docs.agno.com/agent-os)
- [Control Plane](https://docs.agno.com/agent-os/control-plane)
- [Interfaces](https://docs.agno.com/agent-os/interfaces)
- [Segurança](https://docs.agno.com/agent-os/security)

## 🎯 Próximos Passos

Após conectar com sucesso:

1. **Teste o chat** com o agente ARIA-SDR
2. **Configure conhecimento** base
3. **Monitore sessões** e métricas
4. **Implemente interfaces** adicionais
5. **Configure produção** quando necessário
