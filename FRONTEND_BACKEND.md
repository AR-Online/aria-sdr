# 🎨 ARIA-SDR - Frontend + Backend Completo

## ✅ Sistema Completo Rodando

O projeto ARIA-SDR possui **dois componentes** rodando simultaneamente:

### 1. 🔧 **Backend (API FastAPI)**
- **Porta:** 7777
- **URL:** http://localhost:7777
- **Docs:** http://localhost:7777/docs
- **Status:** 🟢 ONLINE

### 2. 🎨 **Frontend (Next.js UI)**
- **Porta:** 3000
- **URL:** http://localhost:3000
- **Tecnologia:** Next.js 15 + React 18 + TypeScript
- **Status:** 🟡 INICIANDO (compilando...)

---

## 🌐 URLs de Acesso

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Frontend (UI)** | http://localhost:3000 | Interface de chat moderna |
| **Backend API** | http://localhost:7777 | API REST do ARIA |
| **API Docs** | http://localhost:7777/docs | Documentação Swagger |
| **Health Check** | http://localhost:7777/healthz | Status da API |

---

## 🎨 O que é o Frontend?

O **Agent UI** é uma interface moderna de chat que permite:

### ✨ Funcionalidades:
- 💬 **Chat em tempo real** com o agente ARIA
- 🔄 **Streaming de respostas** (vê a resposta sendo escrita)
- 📊 **Visualização de tool calls** (quando o agente usa ferramentas)
- 🧠 **Passos de raciocínio** (reasoning steps)
- 📚 **Referências e fontes** utilizadas
- 🖼️ **Suporte multimídia** (imagens, vídeos, áudio)
- 🌓 **Modo escuro/claro**
- 📝 **Histórico de conversas**
- 🎯 **Seleção de agentes** (se houver múltiplos)

### 🛠️ Tecnologias:
- **Framework:** Next.js 15
- **UI Components:** shadcn/ui + Radix UI
- **Styling:** Tailwind CSS
- **Animações:** Framer Motion
- **State:** Zustand
- **Markdown:** react-markdown + remark-gfm

---

## 🔗 Como o Frontend se Conecta ao Backend

O frontend se conecta automaticamente ao backend na porta 7777.

### Configuração do Endpoint:

Por padrão, o Agent UI está configurado para:
```
http://localhost:7777
```

Se precisar mudar:
1. Abra http://localhost:3000
2. No canto superior esquerdo, passe o mouse sobre o endpoint
3. Clique no ícone de editar
4. Altere para o endpoint desejado

---

## 🚀 Como Usar

### 1. Acesse o Frontend
Abra no navegador: **http://localhost:3000**

### 2. Interface Principal
Você verá:
- **Sidebar esquerda:** Lista de agentes e sessões
- **Área central:** Chat com o agente
- **Campo de entrada:** Digite suas mensagens

### 3. Comece a Conversar
Digite qualquer mensagem, por exemplo:
- "Olá, quem é você?"
- "Quero enviar 2000 mensagens para meus clientes"
- "Como funciona o sistema ARIA?"

### 4. Veja as Respostas
O agente ARIA vai responder em tempo real com:
- Classificação de rota (envio/recebimento)
- Análise de volume
- Sugestões personalizadas

---

## 📊 Exemplo de Fluxo

```
Você → Frontend (porta 3000)
         ↓
Frontend → Backend API (porta 7777)
         ↓
Backend → OpenAI GPT-4o-mini
         ↓
Backend → Processa roteamento
         ↓
Backend ← Retorna resposta
         ↓
Frontend ← Recebe stream de resposta
         ↓
Você ← Vê a resposta sendo digitada
```

---

## 🎯 Endpoints Usados pelo Frontend

O frontend faz chamadas para estes endpoints do backend:

| Endpoint | Uso |
|----------|-----|
| `GET /agents` | Lista agentes disponíveis |
| `GET /sessions` | Histórico de conversas |
| `POST /agents/{id}/runs` | Envia mensagem e recebe resposta |
| `GET /healthz` | Verifica status do backend |

---

## 🛑 Como Parar os Serviços

### Frontend:
1. Vá até a janela PowerShell do frontend
2. Pressione `Ctrl+C`

### Backend:
1. Vá até a janela PowerShell do backend
2. Pressione `Ctrl+C`

---

## 🔄 Como Reiniciar

### Backend:
```powershell
cd D:\-ARIA-Agno\aria-platform
python main.py
```

### Frontend:
```powershell
cd D:\-ARIA-Agno\aria-platform\aria-agent-ui
npm run dev
```

---

## 🎨 Customização do Frontend

### Alterar Porta (se necessário):
Edite `aria-agent-ui/package.json`:
```json
"scripts": {
  "dev": "next dev -p 3001"  // Mude 3000 para outra porta
}
```

### Conectar a Outro Backend:
Na interface, clique no endpoint no canto superior esquerdo e altere.

### Temas e Cores:
O frontend usa Tailwind CSS. Edite:
- `aria-agent-ui/tailwind.config.ts` - Cores e temas
- `aria-agent-ui/src/app/globals.css` - Estilos globais

---

## 📱 Screenshots das Funcionalidades

### Interface Principal:
```
┌────────────────────────────────────────────┐
│  [Endpoint: localhost:7777]     [Settings] │
├─────────┬──────────────────────────────────┤
│         │                                  │
│ Agents  │  💬 Chat Area                   │
│ ─────── │                                  │
│ ARIA ✓  │  User: Quero enviar mensagens   │
│         │                                  │
│ History │  ARIA: Olá! Quantas mensagens?  │
│ ─────── │                                  │
│ Today   │                                  │
│ Session │                                  │
│         │                                  │
│         │  [Digite sua mensagem...]   [→] │
└─────────┴──────────────────────────────────┘
```

---

## 🆘 Troubleshooting

### Frontend não carrega (porta 3000)
```powershell
# Verificar se está rodando
netstat -ano | findstr :3000

# Matar processo se necessário
$process = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($process) {
    Stop-Process -Id $process.OwningProcess -Force
}

# Reiniciar
cd aria-agent-ui
npm run dev
```

### "Failed to connect to AgentOS"
- Verifique se o backend está rodando: http://localhost:7777/healthz
- Confirme o endpoint no frontend (canto superior esquerdo)
- Verifique o console do navegador (F12) para erros

### Frontend muito lento
- Next.js compila na primeira vez (15-30 segundos)
- Depois disso, fica rápido
- Se continuar lento, verifique memória RAM disponível

### Erro "Module not found"
```powershell
cd aria-agent-ui
rm -rf node_modules
rm package-lock.json
npm install
```

---

## ✨ Funcionalidades Avançadas

### Streaming de Respostas
O frontend mostra as respostas sendo "digitadas" em tempo real, criando uma experiência mais natural.

### Histórico de Sessões
Todas as conversas são salvas e podem ser acessadas pela sidebar esquerda.

### Múltiplos Agentes
Se você adicionar mais agentes ao backend, eles aparecerão automaticamente na interface.

### Tool Calls Visualization
Quando o agente usa ferramentas (RAG, APIs externas), o frontend mostra:
- Qual ferramenta foi usada
- Os parâmetros
- O resultado

---

## 📚 Documentação Adicional

- **Frontend Code:** `aria-agent-ui/src/`
- **Components:** `aria-agent-ui/src/components/`
- **API Routes:** `aria-agent-ui/src/api/`
- **Hooks:** `aria-agent-ui/src/hooks/`

---

## ✅ Checklist de Funcionalidades

- [x] Backend API rodando (porta 7777)
- [x] Frontend UI rodando (porta 3000)
- [x] OpenAI integrado
- [x] Roteamento inteligente
- [x] Classificação de volume
- [x] Streaming de respostas
- [x] Interface moderna
- [x] Histórico de conversas
- [ ] RAG completo (requer Supabase Service Role Key)

---

## 🎊 Resumo

**Você tem agora um sistema COMPLETO:**

✅ **Backend API FastAPI** → http://localhost:7777  
✅ **Frontend Next.js UI** → http://localhost:3000  
✅ **OpenAI GPT-4o-mini** → Integrado  
✅ **Roteamento Inteligente** → Funcionando  
✅ **Interface Moderna** → Chat em tempo real  

**Tudo pronto para usar! 🚀**

Acesse http://localhost:3000 e comece a conversar com o ARIA!

---

*Última atualização: 2025-10-21*

