# Testes - ARIA Platform

## 📂 Estrutura Organizada

Todos os testes do projeto ARIA foram organizados em uma estrutura clara e hierárquica:

```
tests/
├── integration/          # Testes de integração com serviços externos
│   ├── test_mindchat_integration.py       # Integração completa com Mindchat
│   ├── test_mindchat_real.py              # Testes com API real do Mindchat
│   ├── test_mindchat_specific.py          # Testes específicos do Mindchat
│   ├── test_whatsapp_integration.py       # Integração WhatsApp Business
│   └── test_gitlab_webhook.py             # Webhooks do GitLab
│
├── unit/                 # Testes unitários
│   ├── test_agno_config.py                # Configuração do Agno
│   ├── test_simple.py                     # Testes básicos de funcionalidade
│   └── test_first_os.py                   # Primeiro AgentOS
│
├── setup/                # Testes de configuração e ambiente
│   ├── test_agentos_quick.py              # Teste rápido do AgentOS
│   ├── test_agentos_routes.py             # Rotas do AgentOS
│   ├── teste_env.py                       # Validação de variáveis de ambiente
│   ├── teste_conexoes_mindchat.py         # Conexões com Mindchat
│   └── teste_mindchat_real_token.py       # Token real do Mindchat
│
└── README.md             # Este arquivo
```

## 🚀 Como Executar os Testes

### Todos os testes
```bash
pytest tests/
```

### Por categoria
```bash
# Testes de integração
pytest tests/integration/

# Testes unitários
pytest tests/unit/

# Testes de setup
pytest tests/setup/
```

### Testes específicos
```bash
# Teste específico
pytest tests/integration/test_mindchat_integration.py

# Com verbosidade
pytest tests/integration/test_mindchat_integration.py -v

# Com output detalhado
pytest tests/integration/test_mindchat_integration.py -vv -s
```

## 📋 Tipos de Teste

### 🔗 Testes de Integração
Testam a comunicação com serviços externos:
- **Mindchat API** - Integração com WhatsApp Business
- **GitLab Webhooks** - Notificações de CI/CD
- **WhatsApp** - Mensagens e webhooks

**Requisitos:**
- Tokens de API válidos
- Conexão com internet
- Variáveis de ambiente configuradas

### 🧪 Testes Unitários
Testam funcionalidades isoladas:
- Configuração do Agno
- Funcionalidades básicas
- AgentOS

**Requisitos:**
- Ambiente Python configurado
- Dependências instaladas

### ⚙️ Testes de Setup
Validam configuração do ambiente:
- Variáveis de ambiente
- Tokens de API
- Conexões de rede

**Uso:**
Execute antes de rodar a aplicação para garantir que tudo está configurado.

## 🔧 Configuração

### 1. Instalar dependências de teste
```bash
pip install pytest pytest-cov pytest-asyncio
```

### 2. Configurar variáveis de ambiente
```bash
# Copiar arquivo de exemplo
cp config.env.example .env

# Editar com suas credenciais
# OPENAI_API_KEY=...
# MINDCHAT_API_TOKEN=...
# etc.
```

### 3. Executar testes de setup
```bash
# Validar ambiente
python tests/setup/teste_env.py

# Testar conexões
python tests/setup/teste_conexoes_mindchat.py
```

## 📊 Coverage

Para gerar relatório de cobertura:

```bash
# Executar com coverage
pytest tests/ --cov=. --cov-report=html

# Ver relatório
# Abrir htmlcov/index.html no navegador
```

## 🐛 Debug

Para debug de testes:

```bash
# Com breakpoint
pytest tests/unit/test_simple.py --pdb

# Com logs
pytest tests/ --log-cli-level=DEBUG

# Parar no primeiro erro
pytest tests/ -x
```

## ✅ Boas Práticas

1. **Organize por tipo** - Integration, Unit, Setup
2. **Nomes descritivos** - `test_<funcionalidade>_<cenario>.py`
3. **Docstrings** - Documente o propósito de cada teste
4. **Mocks** - Use mocks para serviços externos em unit tests
5. **Fixtures** - Reutilize configurações com pytest fixtures
6. **Assertions claras** - Mensagens de erro descritivas

## 📝 Convenções

### Nomenclatura
- `test_*.py` - Testes em inglês (padrão pytest)
- `teste_*.py` - Testes em português (específicos do projeto)

### Estrutura de teste
```python
def test_funcionalidade_cenario():
    """Descrição do teste."""
    # Arrange (preparar)
    dados = preparar_dados()
    
    # Act (executar)
    resultado = funcao_testada(dados)
    
    # Assert (validar)
    assert resultado == esperado
```

## 🔄 CI/CD

Os testes são executados automaticamente no pipeline GitLab:
- **Commit** → Testes unitários
- **Merge Request** → Testes de integração
- **Deploy** → Smoke tests

## 📞 Suporte

Para problemas com testes:
1. Verificar configuração do ambiente
2. Validar tokens de API
3. Consultar logs do pytest
4. Abrir issue no GitLab

---

**Última atualização:** 19/10/2025  
**Testes organizados:** ✅ 13 arquivos  
**Cobertura:** Em desenvolvimento
