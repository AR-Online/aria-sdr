# ARIA-SDR Reflector

Versão simplificada do ARIA-SDR com RAG Supabase e regras determinísticas.

## 🚀 Início Rápido

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Ambiente
```bash
cp env.example .env
# Edite o arquivo .env com suas chaves
```

### 3. Executar
```bash
python main.py
```

## 📋 Funcionalidades

- ✅ **RAG Supabase**: Busca inteligente na base de conhecimento
- ✅ **Regras Determinísticas**: Classificação automática de volume
- ✅ **Respostas Calorosas**: Tom WhatsApp brasileiro
- ✅ **AgentOS**: Framework completo de agentes
- ✅ **Endpoint /healthz**: Compatível com interfaces

## 🔧 Configuração

### Variáveis Obrigatórias:
- `OPENAI_API_KEY`: Chave da API OpenAI
- `SUPABASE_URL`: URL do projeto Supabase
- `SUPABASE_SERVICE_ROLE_KEY`: Chave de serviço do Supabase

### Variáveis Opcionais:
- `EMBEDDING_MODEL`: Modelo de embedding (padrão: text-embedding-ada-002)
- `EMBEDDING_DIM`: Dimensão do embedding (padrão: 1536)

## 🎯 Uso

O servidor iniciará na porta 8000 com:
- **Interface AgentOS**: http://localhost:8000
- **Health Check**: http://localhost:8000/healthz
- **API REST**: Endpoints automáticos do AgentOS

## 📚 Base de Conhecimento

A ARIA utiliza uma base de conhecimento no Supabase com:
- Scripts SDR
- Apresentação AR Online
- Manual de Produto
- Exemplos de conversas otimizadas

## 🤖 Personalidade da ARIA

- **Tom**: Conversa natural de WhatsApp
- **Idioma**: Português brasileiro
- **Estilo**: Direta, clara e gentil
- **Regras**: Determinísticas para classificação de volume
- **Roteamento**: Automático baseado em volume mensal

## 🔍 Troubleshooting

### Erro de Importação
```bash
pip install agno openai python-dotenv numpy requests uvicorn
```

### Erro de Conexão Supabase
Verifique as variáveis `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` no arquivo `.env`.

### Erro de Embedding
Certifique-se de que `EMBEDDING_MODEL` e `EMBEDDING_DIM` correspondem aos dados no Supabase.

## 📞 Suporte

Para dúvidas ou problemas, consulte a documentação completa do projeto principal.
