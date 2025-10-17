# ARIA-SDR Reflector - Configuração do Projeto

## 📁 Estrutura do Projeto

```
reflector/
├── main.py              # Servidor principal
├── requirements.txt      # Dependências Python
├── env.example          # Template de configuração
├── README.md            # Documentação
├── setup.py             # Configuração rápida
├── check_setup.py       # Verificação de sistema
├── test_system.py       # Teste de dependências
├── test_api.py          # Teste de API
├── install.sh           # Instalação Linux/Mac
├── install.bat          # Instalação Windows
├── pyproject.toml       # Configuração do projeto
└── .gitignore           # Arquivos ignorados pelo Git
```

## 🚀 Início Rápido

### 1. Instalação Automática
```bash
# Linux/Mac
chmod +x install.sh
./install.sh

# Windows
install.bat
```

### 2. Instalação Manual
```bash
pip install -r requirements.txt
cp env.example .env
# Edite o arquivo .env
python setup.py
```

### 3. Execução
```bash
python main.py
```

## 🔧 Configuração

### Variáveis Obrigatórias (.env):
- `OPENAI_API_KEY`: Chave da API OpenAI
- `SUPABASE_URL`: URL do projeto Supabase
- `SUPABASE_SERVICE_ROLE_KEY`: Chave de serviço do Supabase

### Variáveis Opcionais:
- `EMBEDDING_MODEL`: Modelo de embedding (padrão: text-embedding-ada-002)
- `EMBEDDING_DIM`: Dimensão do embedding (padrão: 1536)
- `APP_ENV`: Ambiente (padrão: development)
- `DEBUG_MODE`: Modo debug (padrão: true)

## 🧪 Testes

### Teste de Sistema:
```bash
python test_system.py
```

### Teste de API:
```bash
python test_api.py
```

### Verificação de Setup:
```bash
python check_setup.py
```

## 📚 Funcionalidades

- ✅ **RAG Supabase**: Busca inteligente na base de conhecimento
- ✅ **Regras Determinísticas**: Classificação automática de volume
- ✅ **Respostas Calorosas**: Tom WhatsApp brasileiro
- ✅ **AgentOS**: Framework completo de agentes
- ✅ **Endpoint /healthz**: Compatível com interfaces
- ✅ **API REST**: Endpoints automáticos do AgentOS

## 🎯 Uso

### Servidor Principal:
- **Porta**: 8000
- **Interface**: http://localhost:8000
- **Health Check**: http://localhost:8000/healthz

### Endpoints Disponíveis:
- `GET /healthz`: Status do servidor
- `POST /chat`: Chat com a ARIA
- `GET /agents`: Lista de agentes
- `GET /memories`: Memórias do usuário

## 🔍 Troubleshooting

### Erro de Importação:
```bash
pip install agno openai python-dotenv numpy requests uvicorn
```

### Erro de Conexão Supabase:
Verifique as variáveis `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` no arquivo `.env`.

### Erro de Embedding:
Certifique-se de que `EMBEDDING_MODEL` e `EMBEDDING_DIM` correspondem aos dados no Supabase.

## 📞 Suporte

Para dúvidas ou problemas, consulte a documentação completa do projeto principal.
