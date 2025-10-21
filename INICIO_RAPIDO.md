# 🚀 Início Rápido - ARIA-SDR (Teste Local)

## ⚡ Em 3 Comandos

```powershell
# 1. Setup automático (cria ambiente, instala dependências)
.\setup_teste_local.ps1

# 2. Adicione sua chave OpenAI no arquivo .env
notepad .env

# 3. Execute o servidor
.\teste_local.ps1
```

## 📝 O que cada script faz?

### 1️⃣ `setup_teste_local.ps1` - Prepara tudo
- ✅ Cria o arquivo `.env` com configurações
- ✅ Cria o ambiente virtual Python
- ✅ Instala todas as dependências
- ✅ Verifica a instalação

### 2️⃣ `teste_local.ps1` - Executa o servidor
- ✅ Ativa o ambiente virtual
- ✅ Verifica configurações
- ✅ Inicia o servidor na porta 7777
- 🌐 Abre a API em `http://localhost:7777`

### 3️⃣ `teste_api.ps1` - Testa a API (opcional)
- 🧪 Executa 5 testes automáticos
- ✅ Verifica se tudo está funcionando
- 📊 Mostra relatório de sucesso

## 🎯 Fluxo Completo

```powershell
# Terminal 1: Preparar e executar servidor
.\setup_teste_local.ps1
notepad .env  # Adicionar OPENAI_API_KEY
.\teste_local.ps1

# Terminal 2: Testar API (em outro terminal)
.\teste_api.ps1
```

## 🔑 Configuração Mínima Obrigatória

Apenas **1 configuração** é obrigatória para começar:

No arquivo `.env`, edite esta linha:
```env
OPENAI_API_KEY=sk-proj-XXXXX  # Sua chave real aqui
```

**Onde conseguir?** https://platform.openai.com/api-keys

## 🌐 URLs Importantes

Quando o servidor estiver rodando:

| URL | Descrição |
|-----|-----------|
| http://localhost:7777 | API Principal |
| http://localhost:7777/docs | 📚 Documentação Swagger (Interface Visual) |
| http://localhost:7777/healthz | ❤️ Health Check |
| http://localhost:7777/redoc | 📖 Documentação ReDoc |

## 🧪 Teste Rápido no Navegador

1. Execute o servidor: `.\teste_local.ps1`
2. Abra: http://localhost:7777/docs
3. Clique em **GET /healthz**
4. Clique em **Try it out**
5. Clique em **Execute**
6. Veja o resultado: `{"ok": true}` ✅

## 🐛 Problemas Comuns

### Erro: "OPENAI_API_KEY não configurada"
```powershell
notepad .env
# Adicione: OPENAI_API_KEY=sk-proj-sua_chave_aqui
```

### Erro: "ModuleNotFoundError"
```powershell
.\agno_env\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Erro: "Porta 7777 já em uso"
```powershell
# Edite .env e mude para outra porta
# PORT=8000
```

### Erro: "Ambiente virtual não encontrado"
```powershell
python -m venv agno_env
```

## 📊 Teste Manual com curl (PowerShell)

```powershell
# 1. Health Check
curl http://localhost:7777/healthz

# 2. Teste de Routing (com autenticação)
$headers = @{
    "Authorization" = "Bearer dtransforma2026"
    "Content-Type" = "application/json"
}

$body = @{
    message = "Olá, preciso de ajuda"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:7777/assist/routing" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

## ✅ Checklist de Início Rápido

- [ ] Executei `.\setup_teste_local.ps1`
- [ ] Adicionei minha `OPENAI_API_KEY` no `.env`
- [ ] Executei `.\teste_local.ps1`
- [ ] Vi "Iniciando ARIA-SDR na porta 7777" no terminal
- [ ] Acessei http://localhost:7777/docs no navegador
- [ ] Testei o endpoint `/healthz` e recebi `{"ok": true}`

## 🎓 Próximos Passos

Depois que tudo estiver funcionando:

1. ✅ Leia o [Guia Completo](TESTE_LOCAL_GUIA.md)
2. ✅ Configure integrações opcionais (Supabase, WhatsApp)
3. ✅ Execute os testes automáticos: `pytest tests/`
4. ✅ Explore a [Documentação da API](http://localhost:7777/docs)

## 📚 Documentação Adicional

- 📖 [Guia de Teste Completo](TESTE_LOCAL_GUIA.md)
- 📘 [README Principal](README.md)
- 🔧 [Configuração Avançada](docs/CONTROL_PLANE_SETUP.md)

## 💡 Dica Pro

Para desenvolvimento, mantenha 2 terminais abertos:

**Terminal 1** (Servidor):
```powershell
.\teste_local.ps1  # Deixar rodando
```

**Terminal 2** (Testes):
```powershell
.\teste_api.ps1    # Executar quando quiser testar
```

---

**🎉 Pronto! Em menos de 5 minutos você está testando a ARIA-SDR localmente!**

💬 Dúvidas? Consulte o [guia completo](TESTE_LOCAL_GUIA.md) ou os [logs do servidor](last_error.log).

