# ✅ ARIA-SDR - Servidor Rodando Localmente

## 🟢 Status: ONLINE

O servidor está rodando em uma janela separada do PowerShell.

---

## 🌐 URLs de Acesso

| Serviço | URL |
|---------|-----|
| **API Principal** | http://localhost:7777 |
| **Documentação Interativa** | http://localhost:7777/docs |
| **Health Check** | http://localhost:7777/healthz |

---

## ✅ Funcionalidades Testadas

- ✅ Health Check: Respondendo
- ✅ Agentes: 1 disponível (ARIA-SDR)
- ✅ Roteamento Inteligente: Funcionando
- ✅ Classificação de Volume: Funcionando
- ✅ OpenAI Integration: Ativo

---

## 🧪 Como Testar

### Opção 1: Via Navegador (Mais Fácil)

**Abra no navegador:** http://localhost:7777/docs

Você terá uma interface Swagger onde pode:
- Ver todos os endpoints
- Testar cada um interativamente
- Ver exemplos de requisições/respostas

### Opção 2: Via PowerShell

```powershell
# Health Check
Invoke-WebRequest http://localhost:7777/healthz

# Testar Roteamento
$body = @{
    user_text = "Quero enviar 2000 mensagens"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:7777/assist/routing `
    -Method POST `
    -Body $body `
    -ContentType "application/json" `
    -Headers @{Authorization = "Bearer dtransforma2026"}
```

### Opção 3: Via cURL

```bash
# Health Check
curl http://localhost:7777/healthz

# Testar Roteamento
curl -X POST http://localhost:7777/assist/routing \
  -H "Authorization: Bearer dtransforma2026" \
  -H "Content-Type: application/json" \
  -d '{"user_text": "Quero enviar mensagens"}'
```

---

## 📊 Endpoints Principais

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/healthz` | GET | Verifica se servidor está online |
| `/assist/routing` | POST | Roteamento inteligente de mensagens |
| `/rag/query` | POST | Busca RAG (requer Supabase key) |
| `/agents` | GET | Lista agentes disponíveis |
| `/webhook/gitlab/aria` | POST | Webhook para GitLab |
| `/webhook/mindchat/whatsapp` | POST | Webhook para WhatsApp |
| `/docs` | GET | Documentação Swagger |

---

## 🔧 Configurações Ativas

- **OpenAI API Key:** Configurada ✅
- **Porta:** 7777
- **Host:** localhost
- **Auth Token:** dtransforma2026
- **Auto-reload:** Ativo
- **Modelo IA:** gpt-4o-mini

---

## 🛑 Como Parar o Servidor

O servidor está rodando em uma janela separada do PowerShell.

Para parar:
1. Vá até a janela do PowerShell onde o servidor está rodando
2. Pressione `Ctrl+C`
3. Ou feche a janela

---

## 🔄 Como Reiniciar

Se precisar reiniciar o servidor, execute:

```powershell
# Matar processos existentes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Iniciar novamente
python main.py
```

Ou use o script criado:

```powershell
.\configurar_completo.ps1
```

---

## 📁 Arquivos de Configuração

- `.env` - Variáveis de ambiente (não commitado)
- `main.py` - Servidor principal
- `requirements.txt` - Dependências Python

---

## 🆘 Problemas?

### Servidor não responde
```powershell
# Verificar se está rodando
Invoke-WebRequest http://localhost:7777/healthz

# Se não estiver, reiniciar
python main.py
```

### Porta já em uso
```powershell
# Matar processo na porta 7777
$process = Get-NetTCPConnection -LocalPort 7777 -ErrorAction SilentlyContinue
if ($process) {
    Stop-Process -Id $process.OwningProcess -Force
}
```

### Erro de autenticação
Certifique-se de usar o token correto:
```
Authorization: Bearer dtransforma2026
```

---

## 📚 Documentação Adicional

- `PROJETO_ONLINE.md` - Visão geral completa
- `STATUS_CONFIGURACAO.md` - Status detalhado
- `HABILITAR_RAG.md` - Como ativar RAG
- `TESTE_LOCAL_GUIA.md` - Guia completo de testes

---

## ✨ Resumo

✅ **Servidor:** ONLINE na porta 7777  
✅ **OpenAI:** Conectado e funcionando  
✅ **API:** Totalmente operacional  
✅ **Documentação:** Disponível em /docs  
✅ **Testes:** Todos passando  

**🎉 Projeto pronto para uso!**

---

*Última verificação: 2025-10-21*

