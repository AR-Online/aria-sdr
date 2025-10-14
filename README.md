# ARIA-SDR - Sistema de Relacionamento Inteligente

## 🚀 Visão Geral

O ARIA-SDR é um sistema de relacionamento inteligente desenvolvido com o framework Agno, substituindo a arquitetura anterior baseada em n8n. O sistema oferece atendimento automatizado via WhatsApp, classificação de volume de envios e roteamento inteligente.

## ✨ Funcionalidades

- **🤖 AgentOS**: Sistema de agentes inteligentes baseado em Agno
- **📱 WhatsApp Integration**: Integração completa com WhatsApp Business API
- **🔍 RAG (Retrieval-Augmented Generation)**: Sistema de busca e resposta inteligente
- **📊 Classificação de Volume**: Detecção automática de alto/baixo volume
- **🎯 Roteamento Inteligente**: Direcionamento para FAQ, agendamento ou loja
- **🔗 Control Plane**: Interface web para gerenciamento

## 🛠️ Tecnologias

- **Framework**: Agno 2.1.4
- **API**: FastAPI + Uvicorn
- **Banco de Dados**: SQLite (dev) / PostgreSQL (prod)
- **IA**: OpenAI GPT-4o-mini
- **RAG**: Supabase + LanceDB
- **Integração**: WhatsApp Business API + Mindchat

## 🚀 Instalação Rápida

### 1. Clonar o Repositório
```bash
git clone https://gitlab.com/lourealiza/aria-sdr.git
cd aria-sdr
```

### 2. Configurar Ambiente Virtual
```bash
# Criar ambiente virtual
python -m venv agno_env

# Ativar (Windows)
agno_env\Scripts\activate

# Ativar (Linux/Mac)
source agno_env/bin/activate
```

### 3. Instalar Dependências
```bash
# Instalar OpenAI compatível PRIMEIRO
pip install 'openai<1.100.0'

# Instalar Agno e dependências
pip install agno fastapi uvicorn
```

### 4. Configurar Variáveis de Ambiente
```bash
# Copiar arquivo de exemplo
cp config.env.example .env

# Editar com suas credenciais
# OPENAI_API_KEY=sk-...
# ASSISTANT_ID=asst-...
# SUPABASE_URL=https://...
# MINDCHAT_API_TOKEN=...
```

### 5. Executar o Sistema
```bash
# Windows PowerShell
.\start_agentos.ps1

# Windows CMD
start_agentos.bat

# Linux/Mac
python aria_first_os.py
```

## 🌐 Acesso ao Sistema

- **API**: http://localhost:7777
- **Documentação**: http://localhost:7777/docs
- **Health Check**: http://localhost:7777/health
- **Control Plane**: https://platform.agno.com

## 📋 Endpoints Principais

### Health Check
```bash
GET /health
```

### RAG Query
```bash
POST /rag/query
{
  "query": "Como funciona o sistema ARIA?",
  "source": "faq",
  "limit": 5
}
```

### Assist Routing
```bash
POST /assist/routing
{
  "user_text": "Preciso de ajuda",
  "channel": "web"
}
```

## 🔧 Configuração Avançada

### Control Plane
1. Acesse https://platform.agno.com
2. Adicione novo OS: `http://localhost:7777`
3. Nome: `ARIA-SDR Development`
4. Tags: `development`, `aria-sdr`, `whatsapp`

### WhatsApp Integration
Configure as variáveis no `.env`:
```bash
WHATSAPP_ACCESS_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_WEBHOOK_URL=your_webhook_url
WHATSAPP_VERIFY_TOKEN=your_verify_token
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Teste específico
pytest tests/test_smoke_api.py -v

# Teste de integração WhatsApp
python test_whatsapp_integration.py
```

## 📊 Monitoramento

### Logs
```bash
# Ver logs do AgentOS
tail -f logs/agentos.log

# Ver logs da API
tail -f logs/api.log
```

### Métricas
- **Health Check**: Status do sistema
- **Performance**: Tempo de resposta
- **Volume**: Classificação de mensagens
- **Routing**: Direcionamento de conversas

## 🚨 Troubleshooting

### Problema: OpenAI Dependency Error
```bash
# Solução: Usar versão compatível
pip uninstall openai -y
pip install openai==1.99.9
pip install agno
```

### Problema: AgentOS não inicia
```bash
# Verificar ambiente virtual
agno_env\Scripts\activate
python -c "import openai; print(openai.__version__)"
```

### Problema: Pipeline GitLab falha
```bash
# Executar linting local
ruff check .
ruff format .
```

## 📚 Documentação

- [Relatório Técnico](RELATORIO_TECNICO_MIGRACAO_ARIA.md)
- [Workflows Migrados](docs/n8n-workflows-migrated.md)
- [Setup Control Plane](docs/CONTROL_PLANE_SETUP.md)
- [Configuração Agno](agno/aria_agent_config.json)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Equipe

- **Desenvolvimento**: AR Online Team
- **Framework**: Agno
- **Integração**: Mindchat + WhatsApp Business API

## 📞 Suporte

Para suporte técnico ou dúvidas:
- **Email**: suporte@ar-online.com.br
- **Documentação**: [docs.agno.com](https://docs.agno.com)
- **Issues**: [GitLab Issues](https://gitlab.com/lourealiza/aria-sdr/-/issues)

---

**ARIA-SDR** - Transformando relacionamentos através da inteligência artificial 🤖✨