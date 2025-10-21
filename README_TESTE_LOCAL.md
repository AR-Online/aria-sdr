# 🧪 README - Teste Local ARIA-SDR

## 📦 Arquivos de Teste Criados

Este diretório contém scripts automatizados para facilitar o teste local da aplicação ARIA-SDR:

### 🔧 Scripts de Setup e Execução

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `setup_teste_local.ps1` | 5.2 KB | 🔧 Setup completo do ambiente |
| `teste_local.ps1` | 3.3 KB | 🚀 Inicia o servidor ARIA |
| `teste_api.ps1` | 5.5 KB | 🧪 Testa endpoints automaticamente |

### 📚 Guias de Documentação

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `INICIO_RAPIDO.md` | 4.3 KB | ⚡ Início em 3 comandos |
| `TESTE_LOCAL_GUIA.md` | 7.0 KB | 📖 Guia completo e detalhado |

---

## 🚀 Início Rápido (3 Passos)

### 1️⃣ Setup Automático
```powershell
.\setup_teste_local.ps1
```
**O que faz:**
- ✅ Cria arquivo `.env` com configurações padrão
- ✅ Cria ambiente virtual Python (`agno_env`)
- ✅ Instala todas as dependências do `requirements.txt`
- ✅ Verifica se tudo está instalado corretamente

### 2️⃣ Configurar Chave OpenAI
```powershell
notepad .env
```
**Edite esta linha:**
```env
OPENAI_API_KEY=sk-YOUR_KEY_HERE
```
Substitua `sk-YOUR_KEY_HERE` pela sua chave real da OpenAI.

**Onde conseguir:** https://platform.openai.com/api-keys

### 3️⃣ Iniciar Servidor
```powershell
.\teste_local.ps1
```
**O que acontece:**
- ✅ Ativa ambiente virtual automaticamente
- ✅ Verifica configurações
- ✅ Inicia servidor na porta 7777
- 🌐 API disponível em `http://localhost:7777`

---

## 🧪 Testando a API

### Opção A: Testes Automáticos (Recomendado)

Em **outro terminal**:
```powershell
.\teste_api.ps1
```

**Resultado:**
```
✅ Teste 1/5: Health Check - Sucesso!
✅ Teste 2/5: Autenticação - Sucesso!
✅ Teste 3/5: Routing Simples - Sucesso!
✅ Teste 4/5: Baixo Volume - Sucesso!
✅ Teste 5/5: Alto Volume - Sucesso!

🎉 Todos os testes passaram! (100%)
```

### Opção B: Interface Visual (Swagger UI)

Abra no navegador:
```
http://localhost:7777/docs
```

**Como usar:**
1. Escolha um endpoint (ex: GET /healthz)
2. Clique em "Try it out"
3. Clique em "Execute"
4. Veja o resultado abaixo

### Opção C: Teste Manual (curl/PowerShell)

```powershell
# Health Check
curl http://localhost:7777/healthz

# Routing com autenticação
$headers = @{
    "Authorization" = "Bearer dtransforma2026"
    "Content-Type" = "application/json"
}

$body = @{
    message = "Olá, preciso de ajuda"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:7777/assist/routing" `
    -Method POST -Headers $headers -Body $body
```

---

## 🎯 Fluxo de Desenvolvimento

### Primeira Vez (Setup)
```powershell
# 1. Setup completo
.\setup_teste_local.ps1

# 2. Configurar OpenAI
notepad .env  # Adicionar OPENAI_API_KEY

# 3. Testar
.\teste_local.ps1
```

### Desenvolvimento Diário
```powershell
# Terminal 1: Servidor (deixar rodando)
.\teste_local.ps1

# Terminal 2: Testes (executar quando quiser)
.\teste_api.ps1
```

---

## 🌐 URLs Importantes

Quando o servidor estiver rodando:

| URL | Descrição | Método |
|-----|-----------|--------|
| http://localhost:7777 | API Principal | - |
| http://localhost:7777/docs | 📚 Swagger UI (Interface Visual) | GET |
| http://localhost:7777/redoc | 📖 ReDoc (Documentação) | GET |
| http://localhost:7777/healthz | ❤️ Health Check | GET |
| http://localhost:7777/assist/routing | 🤖 Endpoint Principal | POST |
| http://localhost:7777/rag/query | 🔍 RAG Query | POST |

---

## 🔧 Configuração Detalhada

### Configuração Mínima (Obrigatória)

Apenas **1 variável** é obrigatória:
```env
OPENAI_API_KEY=sk-proj-...
```

### Configuração Completa (Opcional)

Para funcionalidades avançadas, configure no `.env`:

#### RAG/Supabase
```env
RAG_ENABLE=true
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sua_chave_aqui
```

#### WhatsApp/Mindchat
```env
MINDCHAT_API_TOKEN=seu_token_aqui
WHATSAPP_ACCESS_TOKEN=seu_token_aqui
WHATSAPP_PHONE_NUMBER_ID=seu_id_aqui
```

#### Servidor
```env
HOST=localhost      # Altere para 0.0.0.0 para aceitar conexões externas
PORT=7777          # Altere se a porta estiver em uso
API_DEBUG=true     # Modo debug (mais logs)
```

---

## 📊 Estrutura dos Scripts

### `setup_teste_local.ps1`
```
1. Verifica/cria .env
2. Verifica/cria agno_env
3. Ativa ambiente virtual
4. Instala dependências
5. Valida instalação
```

### `teste_local.ps1`
```
1. Ativa ambiente virtual
2. Verifica Python
3. Verifica .env
4. Verifica OPENAI_API_KEY
5. Instala dependências faltantes
6. Inicia servidor (main.py)
```

### `teste_api.ps1`
```
1. Testa /healthz
2. Testa /auth_debug
3. Testa /assist/routing (simples)
4. Testa /assist/routing (baixo volume)
5. Testa /assist/routing (alto volume)
6. Gera relatório
```

---

## 🐛 Troubleshooting

### ❌ Erro: "OpenAI API Key não configurada"
```powershell
notepad .env
# Adicione: OPENAI_API_KEY=sk-proj-sua_chave_aqui
```

### ❌ Erro: "ModuleNotFoundError: No module named 'fastapi'"
```powershell
.\agno_env\Scripts\Activate.ps1
pip install -r requirements.txt
```

### ❌ Erro: "Porta 7777 já em uso"
```powershell
# Opção 1: Encontrar e matar processo
netstat -ano | findstr :7777
taskkill /PID <PID> /F

# Opção 2: Usar outra porta
# Edite .env: PORT=8000
```

### ❌ Erro: "Cannot find path 'agno_env'"
```powershell
python -m venv agno_env
.\agno_env\Scripts\Activate.ps1
pip install -r requirements.txt
```

### ❌ Erro: "Unauthorized" nos testes
Certifique-se de usar o token correto:
```
Authorization: Bearer dtransforma2026
```

---

## 📝 Logs e Debug

### Ver Logs do Servidor
Os logs aparecem no terminal onde você executou `.\teste_local.ps1`

### Modo Debug
Edite `.env`:
```env
API_DEBUG=true
API_LOG_LEVEL=debug
```

### Logs de Erro
Erros são salvos em:
- `last_error.log` - Último erro não tratado
- `assist_debug.log` - Debug do endpoint de routing

---

## ✅ Checklist Completo

### Setup Inicial
- [ ] Executei `.\setup_teste_local.ps1`
- [ ] Ambiente virtual criado em `agno_env/`
- [ ] Arquivo `.env` existe
- [ ] Adicionei `OPENAI_API_KEY` no `.env`
- [ ] Dependências instaladas (fastapi, uvicorn, openai, etc.)

### Servidor Funcionando
- [ ] Executei `.\teste_local.ps1`
- [ ] Vi "Iniciando ARIA-SDR na porta 7777"
- [ ] Servidor não mostrou erros
- [ ] Servidor está rodando (não fechou)

### Testes Básicos
- [ ] Acessei http://localhost:7777/docs no navegador
- [ ] Interface Swagger carregou corretamente
- [ ] Testei GET /healthz e recebi `{"ok": true}`
- [ ] Executei `.\teste_api.ps1` com sucesso

### Testes Avançados
- [ ] Testei POST /assist/routing com autenticação
- [ ] Recebi resposta com `reply_text`, `route`, `thread_id`
- [ ] Testei diferentes volumes (baixo/alto)
- [ ] Classificação de volume funcionou corretamente

---

## 🎓 Próximos Passos

Depois de testar localmente com sucesso:

1. **Explorar Endpoints**
   - Leia a documentação em http://localhost:7777/docs
   - Teste diferentes cenários
   - Entenda a estrutura das respostas

2. **Configurar Integrações**
   - RAG/Supabase para respostas inteligentes
   - WhatsApp/Mindchat para mensagens
   - GitLab webhooks para CI/CD

3. **Executar Testes Unitários**
   ```powershell
   pytest tests/ -v
   ```

4. **Deploy em Produção**
   - Configurar variáveis de ambiente de produção
   - Deploy no Cloudflare Workers ou similar
   - Configurar domínio e SSL

---

## 📚 Documentação Adicional

- 📖 [Guia Início Rápido](INICIO_RAPIDO.md) - 3 comandos para começar
- 📘 [Guia Completo de Teste](TESTE_LOCAL_GUIA.md) - Guia detalhado
- 📕 [README Principal](README.md) - Visão geral do projeto
- 🔧 [Control Plane Setup](docs/CONTROL_PLANE_SETUP.md) - Configuração AgentOS
- 📱 [Integração Mindchat](docs/MINDCHAT_INTEGRATION.md) - WhatsApp integration

---

## 💡 Dicas Profissionais

### Desenvolvimento Eficiente

1. **Use 2 Terminais**
   - Terminal 1: Servidor (`.\teste_local.ps1`)
   - Terminal 2: Testes (`.\teste_api.ps1`)

2. **Hot Reload**
   O servidor usa uvicorn com `reload=True`, então ele reinicia automaticamente quando você edita o código.

3. **Swagger UI é seu amigo**
   Use http://localhost:7777/docs para explorar e testar rapidamente.

4. **Valide tokens**
   Todos os endpoints protegidos usam: `Bearer dtransforma2026`

### Performance

1. **RAG opcional**
   Para testes básicos, deixe `RAG_ENABLE=false` para melhor performance

2. **OpenAI timeout**
   Ajuste `ASSISTANT_TIMEOUT_SECONDS` se necessário (padrão: 12s)

3. **Log level**
   Use `API_LOG_LEVEL=info` em produção, `debug` só para desenvolvimento

---

## 🆘 Suporte

### Precisa de Ajuda?

1. **Verifique os logs** no terminal do servidor
2. **Consulte o guia completo**: `TESTE_LOCAL_GUIA.md`
3. **Verifique problemas comuns** na seção Troubleshooting acima
4. **Teste cada componente** individualmente:
   ```powershell
   python -c "import fastapi; print('FastAPI OK')"
   python -c "import openai; print('OpenAI OK')"
   ```

### Issues Conhecidos

- **Python 3.13.7**: Totalmente compatível ✅
- **Windows PowerShell**: Todos os scripts testados ✅
- **OpenAI SDK**: Use versão >= 1.40.0 ✅

---

## 📊 Status dos Componentes

| Componente | Status | Obrigatório |
|------------|--------|-------------|
| FastAPI | ✅ Instalado | ✅ Sim |
| Uvicorn | ✅ Instalado | ✅ Sim |
| OpenAI | ✅ Instalado | ✅ Sim (API Key) |
| Supabase | ⚠️ Opcional | ❌ Não |
| Mindchat | ⚠️ Opcional | ❌ Não |
| WhatsApp | ⚠️ Opcional | ❌ Não |

---

**🎉 Você está pronto para testar a ARIA-SDR localmente!**

Execute agora:
```powershell
.\setup_teste_local.ps1
```

💬 Boa sorte e bons testes! 🚀

