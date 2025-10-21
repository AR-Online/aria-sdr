# 🧪 Guia de Teste Local Manual - ARIA-SDR

Este guia vai te ajudar a testar a aplicação ARIA-SDR localmente no seu computador.

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter:

- ✅ Python 3.8+ instalado (você tem Python 3.13.7 ✓)
- ✅ Uma chave da API da OpenAI (obtenha em <https://platform.openai.com/>)
- ✅ Git instalado
- ✅ Terminal/PowerShell

## 🚀 Passo a Passo - Configuração Inicial

### 1. Preparar o Ambiente Virtual (se ainda não fez)

```powershell
# Se o ambiente virtual já existe, pule esta etapa
python -m venv agno_env
```

### 2. Ativar o Ambiente Virtual

```powershell
# Windows PowerShell
.\agno_env\Scripts\Activate.ps1

# Você verá (agno_env) no início do prompt quando ativado
```

### 3. Instalar Dependências

```powershell
# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências do projeto
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Já criei um arquivo `.env` para você! Agora você precisa adicionar sua chave da OpenAI:

```powershell
# Abra o arquivo .env com seu editor favorito
notepad .env

# Ou use o VSCode
code .env
```

**IMPORTANTE**: Encontre esta linha no arquivo `.env`:

```env
OPENAI_API_KEY=sk-YOUR_KEY_HERE
```

E substitua `sk-YOUR_KEY_HERE` pela sua chave real da OpenAI.

## 🎯 Executar a Aplicação

### Opção 1: Script Automático (Recomendado)

Criei um script que faz tudo automaticamente:

```powershell
.\teste_local.ps1
```

Este script vai:

- ✅ Verificar o ambiente virtual
- ✅ Ativar o ambiente automaticamente
- ✅ Verificar as dependências
- ✅ Validar a configuração
- ✅ Iniciar o servidor ARIA-SDR

### Opção 2: Manual

```powershell
# 1. Ativar ambiente virtual
.\agno_env\Scripts\Activate.ps1

# 2. Executar o servidor
python main.py
```

## 🧪 Testar a Aplicação

Quando o servidor estiver rodando, você verá algo assim:

```
Iniciando ARIA-SDR na porta 7777
Interface: http://localhost:3000
API: http://localhost:7777
Docs: http://localhost:7777/docs
```

### Teste 1: Health Check

Abra um **novo terminal** e execute:

```powershell
# Teste básico de saúde
curl http://localhost:7777/healthz
```

Resposta esperada:
```json
{"ok": true}
```

### Teste 2: Interface Swagger (Documentação Interativa)

Abra seu navegador e acesse:

```
http://localhost:7777/docs
```

Aqui você pode testar todos os endpoints visualmente!

### Teste 3: Endpoint de Routing (Principal)

```powershell
# Usando curl (PowerShell)
$headers = @{
    "Authorization" = "Bearer dtransforma2026"
    "Content-Type" = "application/json"
}

$body = @{
    message = "Olá, preciso enviar 500 mensagens"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:7777/assist/routing" -Method POST -Headers $headers -Body $body
```

### Teste 4: RAG Query (Sistema de Perguntas)

**Nota**: Este teste só funciona se você configurou o Supabase. Se não configurou, é normal dar erro.

```powershell
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    question = "Como funciona o sistema ARIA?"
    k = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:7777/rag/query" -Method POST -Headers $headers -Body $body
```

## 📊 Testes Disponíveis na Interface Swagger

Acesse `http://localhost:7777/docs` e teste:

1. **GET /healthz** - Verifica se o servidor está funcionando
2. **POST /assist/routing** - Endpoint principal de roteamento
3. **POST /rag/query** - Sistema de perguntas e respostas
4. **GET /auth_debug** - Testa autenticação

### Como usar o Swagger UI:

1. Clique no endpoint que quer testar (ex: `/healthz`)
2. Clique em "Try it out"
3. Preencha os parâmetros necessários
4. Clique em "Execute"
5. Veja a resposta abaixo

## 🔧 Configurações Opcionais

### Habilitar RAG (Sistema de Respostas Inteligentes)

Se você tem acesso ao Supabase, edite o `.env`:

```env
RAG_ENABLE=true
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sua_chave_aqui
```

### Habilitar WhatsApp/Mindchat

Se você tem credenciais do Mindchat, edite o `.env`:

```env
MINDCHAT_API_TOKEN=seu_token_aqui
WHATSAPP_ACCESS_TOKEN=seu_token_aqui
```

## 🐛 Resolução de Problemas

### Problema: "ModuleNotFoundError"

```powershell
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Problema: "Unauthorized" ao testar endpoints

Certifique-se de usar o token correto no header:
```
Authorization: Bearer dtransforma2026
```

### Problema: Porta 7777 já em uso

Edite o `.env` e mude a porta:
```env
PORT=8000
```

E reinicie o servidor.

### Problema: OpenAI API Error

1. Verifique se sua chave está correta no `.env`
2. Verifique se tem créditos na sua conta OpenAI
3. Teste sua chave em: <https://platform.openai.com/>

## 📝 Logs e Debugging

Os logs aparecem no terminal onde você executou o servidor. Para modo debug mais detalhado, edite o `.env`:

```env
API_DEBUG=true
API_LOG_LEVEL=debug
```

## 🎓 Próximos Passos

Depois de testar localmente com sucesso:

1. ✅ Configurar variáveis de produção
2. ✅ Configurar Supabase para RAG
3. ✅ Integrar com WhatsApp/Mindchat
4. ✅ Deploy em produção (Cloudflare Workers ou similar)

## 📚 Documentação Adicional

- [README principal](README.md)
- [Documentação da API](http://localhost:7777/docs) (quando o servidor estiver rodando)
- [Configuração Control Plane](docs/CONTROL_PLANE_SETUP.md)
- [Integração Mindchat](docs/MINDCHAT_INTEGRATION.md)

## 💡 Comandos Úteis

```powershell
# Ver dependências instaladas
pip list

# Verificar se OpenAI está instalada
python -c "import openai; print(openai.__version__)"

# Verificar se FastAPI está instalada
python -c "import fastapi; print(fastapi.__version__)"

# Parar o servidor
# Pressione Ctrl+C no terminal onde o servidor está rodando

# Desativar ambiente virtual
deactivate
```

## ✅ Checklist de Teste

Use esta checklist para garantir que tudo está funcionando:

- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (pip install -r requirements.txt)
- [ ] Arquivo .env configurado com OPENAI_API_KEY
- [ ] Servidor inicia sem erros (python main.py)
- [ ] Health check retorna {"ok": true}
- [ ] Interface Swagger acessível em /docs
- [ ] Endpoint /assist/routing responde corretamente
- [ ] Autenticação funciona com Bearer token

## 🆘 Precisa de Ajuda?

Se encontrar problemas:

1. Verifique os logs no terminal
2. Confirme que o ambiente virtual está ativado
3. Verifique se todas as dependências estão instaladas
4. Confirme que a porta 7777 está livre
5. Verifique se sua chave OpenAI está válida

---

**Boa sorte com os testes! 🚀**

