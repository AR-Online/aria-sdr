# 🔧 Como Limpar o Cache e Resolver o Erro "Failed to fetch"

## ❌ Problema
O erro `TypeError: Failed to fetch` ocorre porque o navegador está usando uma versão em cache do frontend que ainda tenta conectar na porta **8000** (antiga), mas o backend está na porta **7777** (nova).

## ✅ Solução - Passo a Passo

### **Método 1: Limpar localStorage (RECOMENDADO)**

1. **Abra o site:** http://localhost:3000

2. **Abra o DevTools:**
   - Pressione `F12` (Windows/Linux)
   - Ou `Cmd + Option + I` (Mac)

3. **Vá na aba "Console"**

4. **Execute este comando:**
   ```javascript
   localStorage.clear()
   ```

5. **Recarregue a página:**
   - Pressione `Ctrl + Shift + R` (Windows/Linux)
   - Ou `Cmd + Shift + R` (Mac)

---

### **Método 2: Limpar Cache do Navegador**

1. **No Chrome/Edge:**
   - Abra DevTools (`F12`)
   - Clique com botão direito no ícone de recarregar
   - Selecione "Limpar cache e recarregar forçado"

2. **No Firefox:**
   - Pressione `Ctrl + Shift + Delete`
   - Selecione "Cache"
   - Clique em "Limpar agora"

---

### **Método 3: Modo Anônimo (Teste Rápido)**

1. Abra uma janela anônima/privada
2. Acesse: http://localhost:3000
3. Teste o chat

---

## 🔍 Como Verificar se Funcionou

Após limpar o cache:

1. **Abra DevTools (`F12`)**
2. **Vá na aba "Network"**
3. **Envie uma mensagem no chat**
4. **Verifique se a requisição vai para:**
   ```
   http://localhost:7777/agents/aria-sdr/runs
   ```
   ✅ Se for para `7777` = **CORRETO**
   ❌ Se for para `8000` = Cache ainda ativo, repita os passos

---

## 📝 Verificação Final

Se ainda não funcionar:

1. **Pare o frontend:**
   - Pressione `Ctrl + C` no terminal do frontend

2. **Limpe o cache do Next.js:**
   ```powershell
   cd aria-agent-ui
   Remove-Item -Recurse -Force .next
   ```

3. **Reinicie o frontend:**
   ```powershell
   npm run dev
   ```

4. **Abra em modo anônimo:**
   - http://localhost:3000

---

## ✅ Confirmar que está Tudo Certo

Backend:
- ✅ http://localhost:7777/healthz deve retornar `{"ok":true}`

Frontend:
- ✅ http://localhost:3000 deve carregar a interface
- ✅ Ao enviar mensagem, deve conectar em `localhost:7777`

---

## 🆘 Ainda com Problemas?

Execute este comando para verificar os servidores:

```powershell
# Verificar portas em uso
Get-NetTCPConnection | Where-Object {$_.LocalPort -eq 3000 -or $_.LocalPort -eq 7777} | Select-Object LocalPort, State, OwningProcess
```

Backend deve estar na porta **7777**  
Frontend deve estar na porta **3000**

