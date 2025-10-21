# 📚 Índice Completo de Documentação - ARIA-SDR

Este arquivo consolida toda a documentação do projeto ARIA-SDR para fácil navegação.

---

## 🚀 Início Rápido

**Para começar imediatamente**, leia nesta ordem:

1. **[COMECE_AQUI.txt](COMECE_AQUI.txt)** - Checklist visual rápido
2. **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** - 3 comandos para começar
3. **[TESTE_LOCAL_GUIA.md](TESTE_LOCAL_GUIA.md)** - Guia completo de teste

**Tempo estimado**: 15 minutos para setup completo

---

## 📖 Documentação Principal

### Geral

| Documento | Descrição | Quando Ler |
|-----------|-----------|------------|
| [README.md](README.md) | Visão geral do projeto | Primeiro contato |
| [CHANGELOG.md](CHANGELOG.md) | Histórico de mudanças | Ver atualizações |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Guia de contribuição | Antes de contribuir |
| [LICENSE](LICENSE) | Licença do projeto | Questões legais |

### Setup e Configuração

| Documento | Descrição | Quando Ler |
|-----------|-----------|------------|
| [COMECE_AQUI.txt](COMECE_AQUI.txt) | Checklist de início rápido | Primeira vez |
| [INICIO_RAPIDO.md](INICIO_RAPIDO.md) | Setup em 3 comandos | Primeira vez |
| [TESTE_LOCAL_GUIA.md](TESTE_LOCAL_GUIA.md) | Guia completo de teste local | Setup detalhado |
| [README_TESTE_LOCAL.md](README_TESTE_LOCAL.md) | README técnico de testes | Referência técnica |
| [config.env.example](config.env.example) | Template de configuração | Configurar .env |

### Relatórios e Análises

| Documento | Descrição | Quando Ler |
|-----------|-----------|------------|
| [RELATORIO_ANALISE_COMPLETA_ARIA.md](RELATORIO_ANALISE_COMPLETA_ARIA.md) | ⭐ Análise completa do sistema | Para entender status |
| [RELATORIO_TECNICO_MIGRACAO_ARIA.md](RELATORIO_TECNICO_MIGRACAO_ARIA.md) | Análise da migração n8n→Agno | Contexto histórico |
| [RELATORIO_COMPLETO_ARIA_AGNO.md](RELATORIO_COMPLETO_ARIA_AGNO.md) | Relatório completo Agno | Detalhes Agno |
| [RESUMO_EXECUTIVO_ARIA_AGNO.md](RESUMO_EXECUTIVO_ARIA_AGNO.md) | Resumo executivo | Visão executiva |

### Guias Técnicos

| Documento | Descrição | Quando Ler |
|-----------|-----------|------------|
| [GUIA_AGNO_FRAMEWORK.md](GUIA_AGNO_FRAMEWORK.md) | ⭐ Guia completo do Agno | Trabalhar com Agno |
| [CHECKLIST_PRODUCAO.md](CHECKLIST_PRODUCAO.md) | ⭐ Checklist de produção | Antes de deploy |
| [ANALISE_TESTES.md](ANALISE_TESTES.md) | Análise dos testes | Melhorar testes |
| [ANALISE_DUPLICATAS.md](ANALISE_DUPLICATAS.md) | Análise de duplicatas | Limpeza de código |

### Deploy e Infraestrutura

| Documento | Descrição | Quando Ler |
|-----------|-----------|------------|
| [README_DEPLOY.md](README_DEPLOY.md) | Guia de deploy | Deploy produção |
| [DEPLOY_OPTIONS.md](DEPLOY_OPTIONS.md) | Opções de deploy | Escolher plataforma |
| [SIMPLE_DEPLOY.md](SIMPLE_DEPLOY.md) | Deploy simplificado | Deploy rápido |
| [CLOUDFLARE_DEPLOY.md](CLOUDFLARE_DEPLOY.md) | Deploy no Cloudflare | Deploy Cloudflare |
| [README.Docker.md](README.Docker.md) | Uso com Docker | Deploy Docker |
| [docker-compose.yml](docker-compose.yml) | Configuração Docker Compose | Ambiente Docker |
| [Dockerfile](Dockerfile) | Dockerfile de desenvolvimento | Build dev |
| [Dockerfile.prod](Dockerfile.prod) | Dockerfile de produção | Build prod |

### Integrações

| Documento | Descrição | Quando Ler |
|-----------|-----------|------------|
| [docs/INTEGRATION.md](docs/INTEGRATION.md) | Guia de integrações | Integrar sistemas |
| [docs/MINDCHAT_INTEGRATION.md](docs/MINDCHAT_INTEGRATION.md) | Integração Mindchat | Setup WhatsApp |
| [GUIA_TESTE_MINDCHAT.md](GUIA_TESTE_MINDCHAT.md) | Teste Mindchat | Testar WhatsApp |
| [docs/GITLAB_WEBHOOK_INTEGRATION.md](docs/GITLAB_WEBHOOK_INTEGRATION.md) | Webhooks GitLab | Setup CI/CD |
| [GITLAB_SETUP.md](GITLAB_SETUP.md) | Setup GitLab | Configurar GitLab |
| [GITLAB_VARIABLES_SETUP.md](GITLAB_VARIABLES_SETUP.md) | Variáveis GitLab | CI/CD vars |
| [SOLUCAO_WEBHOOK_404.md](SOLUCAO_WEBHOOK_404.md) | Resolver erro 404 | Troubleshoot |

### Arquitetura

| Documento | Descrição | Quando Ler |
|-----------|-----------|------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura do sistema | Entender estrutura |
| [docs/n8n-workflows-migrated.md](docs/n8n-workflows-migrated.md) | Workflows migrados | Contexto migração |
| [docs/CONTROL_PLANE_SETUP.md](docs/CONTROL_PLANE_SETUP.md) | Setup Control Plane | Agno Control Plane |
| [docs/AGNO_OPTIMIZATION_PLAN.md](docs/AGNO_OPTIMIZATION_PLAN.md) | Plano de otimização | Otimizar Agno |

---

## 🛠️ Scripts e Ferramentas

### Scripts PowerShell

| Script | Descrição | Uso |
|--------|-----------|-----|
| [setup_teste_local.ps1](setup_teste_local.ps1) | Setup automático | `.\setup_teste_local.ps1` |
| [teste_local.ps1](teste_local.ps1) | Iniciar servidor | `.\teste_local.ps1` |
| [teste_api.ps1](teste_api.ps1) | Testar endpoints | `.\teste_api.ps1` |
| [iniciar_servidor.ps1](iniciar_servidor.ps1) | Alternativa de start | `.\iniciar_servidor.ps1` |
| [teste_mindchat.ps1](teste_mindchat.ps1) | Testar Mindchat | `.\teste_mindchat.ps1` |
| [start_agentos.ps1](start_agentos.ps1) | Iniciar AgentOS | `.\start_agentos.ps1` |
| [setup_gitlab.ps1](setup_gitlab.ps1) | Setup GitLab | `.\setup_gitlab.ps1` |

### Scripts Python

| Script | Descrição | Uso |
|--------|-----------|-----|
| [check_env.py](check_env.py) | Verificar ambiente | `python check_env.py` |
| [check_environment.py](check_environment.py) | Verificar config | `python check_environment.py` |
| [ingest_faqs.py](ingest_faqs.py) | Ingerir FAQs | `python ingest_faqs.py` |
| [ingest_supabase.py](ingest_supabase.py) | Ingerir Supabase | `python ingest_supabase.py` |
| [monitor_aria.py](monitor_aria.py) | Monitorar sistema | `python monitor_aria.py` |
| [verificar_webhooks.py](verificar_webhooks.py) | Verificar webhooks | `python verificar_webhooks.py` |

---

## 🧪 Testes

### Arquivos de Teste

| Arquivo | Descrição | Executar |
|---------|-----------|----------|
| [tests/test_smoke_api.py](tests/test_smoke_api.py) | Testes básicos de API | `pytest tests/test_smoke_api.py` |
| [tests/test_routing_logic.py](tests/test_routing_logic.py) | Testes de roteamento | `pytest tests/test_routing_logic.py` |
| [tests/test_migration_equivalence.py](tests/test_migration_equivalence.py) | Equivalência migração | `pytest tests/test_migration_equivalence.py` |
| [tests/test_thread_id_precedence.py](tests/test_thread_id_precedence.py) | Thread ID | `pytest tests/test_thread_id_precedence.py` |
| [tests/conftest.py](tests/conftest.py) | Configuração pytest | - |
| [tests/README.md](tests/README.md) | Documentação testes | - |

### Executar Testes

```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/test_smoke_api.py -v

# Com coverage
pytest --cov=. --cov-report=html

# Apenas um teste
pytest tests/test_smoke_api.py::test_healthz_reachable -v
```

---

## 📁 Estrutura de Diretórios

### Diretórios Principais

```
aria-platform/
├── agno/                   # Configurações e agentes Agno
├── api/                    # API alternativa
├── aria-agent-ui/          # Frontend Next.js
├── docs/                   # Documentação adicional
├── functions/              # Cloudflare Functions
├── k8s/                    # Configurações Kubernetes
├── prompts/                # Prompts do sistema
├── reflector/              # Ferramenta reflector
├── scripts/                # Scripts de automação
├── tests/                  # Testes automatizados
└── tmp/                    # Arquivos temporários
```

### Arquivos de Configuração

| Arquivo | Descrição |
|---------|-----------|
| [pyproject.toml](pyproject.toml) | Config Python/Poetry |
| [requirements.txt](requirements.txt) | Dependências Python |
| [requirements-dev.txt](requirements-dev.txt) | Dependências dev |
| [pyrightconfig.json](pyrightconfig.json) | Config Pyright |
| [agno_config.yaml](agno_config.yaml) | Config Agno principal |
| [package.json](package.json) | Config Node.js |
| [Makefile](Makefile) | Comandos make |

---

## 🎯 Guias por Caso de Uso

### Estou Começando do Zero

1. Leia: [COMECE_AQUI.txt](COMECE_AQUI.txt)
2. Execute: [INICIO_RAPIDO.md](INICIO_RAPIDO.md)
3. Siga: [TESTE_LOCAL_GUIA.md](TESTE_LOCAL_GUIA.md)

### Quero Entender o Projeto

1. Leia: [README.md](README.md)
2. Analise: [RELATORIO_ANALISE_COMPLETA_ARIA.md](RELATORIO_ANALISE_COMPLETA_ARIA.md)
3. Estude: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

### Preciso Fazer Deploy

1. Prepare: [CHECKLIST_PRODUCAO.md](CHECKLIST_PRODUCAO.md)
2. Escolha: [DEPLOY_OPTIONS.md](DEPLOY_OPTIONS.md)
3. Execute: [README_DEPLOY.md](README_DEPLOY.md)

### Vou Trabalhar com Agno

1. Leia: [GUIA_AGNO_FRAMEWORK.md](GUIA_AGNO_FRAMEWORK.md)
2. Veja exemplos: [agno/aria_agent_optimized.py](agno/aria_agent_optimized.py)
3. Configure: [agno/agentos_config.yaml](agno/agentos_config.yaml)

### Preciso Integrar WhatsApp

1. Leia: [docs/MINDCHAT_INTEGRATION.md](docs/MINDCHAT_INTEGRATION.md)
2. Siga: [GUIA_TESTE_MINDCHAT.md](GUIA_TESTE_MINDCHAT.md)
3. Configure: [config.env.example](config.env.example)

### Quero Contribuir

1. Leia: [CONTRIBUTING.md](CONTRIBUTING.md)
2. Entenda: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. Teste: [tests/README.md](tests/README.md)

### Encontrei um Problema

1. Verifique: [SOLUCAO_WEBHOOK_404.md](SOLUCAO_WEBHOOK_404.md)
2. Consulte: [TESTE_LOCAL_GUIA.md](TESTE_LOCAL_GUIA.md) (seção Troubleshooting)
3. Leia logs: `last_error.log`, `assist_debug.log`

---

## 🔍 Busca Rápida

### Por Tópico

**Configuração**:
- [config.env.example](config.env.example)
- [TESTE_LOCAL_GUIA.md](TESTE_LOCAL_GUIA.md)
- [agno_config.yaml](agno_config.yaml)

**Agno Framework**:
- [GUIA_AGNO_FRAMEWORK.md](GUIA_AGNO_FRAMEWORK.md) ⭐
- [agno/aria_agent_optimized.py](agno/aria_agent_optimized.py)
- [docs/AGNO_OPTIMIZATION_PLAN.md](docs/AGNO_OPTIMIZATION_PLAN.md)

**API e Endpoints**:
- [main.py](main.py)
- [api/main.py](api/main.py)
- [tests/test_smoke_api.py](tests/test_smoke_api.py)

**RAG e Conhecimento**:
- [ingest_faqs.py](ingest_faqs.py)
- [ingest_supabase.py](ingest_supabase.py)
- [docs/aria_vector_store/](docs/aria_vector_store/)

**WhatsApp e Mindchat**:
- [docs/MINDCHAT_INTEGRATION.md](docs/MINDCHAT_INTEGRATION.md)
- [GUIA_TESTE_MINDCHAT.md](GUIA_TESTE_MINDCHAT.md)
- [teste_mindchat.ps1](teste_mindchat.ps1)

**Deploy e Produção**:
- [CHECKLIST_PRODUCAO.md](CHECKLIST_PRODUCAO.md) ⭐
- [README_DEPLOY.md](README_DEPLOY.md)
- [DEPLOY_OPTIONS.md](DEPLOY_OPTIONS.md)

**GitLab CI/CD**:
- [GITLAB_SETUP.md](GITLAB_SETUP.md)
- [GITLAB_VARIABLES_SETUP.md](GITLAB_VARIABLES_SETUP.md)
- [docs/GITLAB_WEBHOOK_INTEGRATION.md](docs/GITLAB_WEBHOOK_INTEGRATION.md)

**Frontend**:
- [aria-agent-ui/README.md](aria-agent-ui/README.md)
- [aria-agent-ui/package.json](aria-agent-ui/package.json)

---

## 📊 Estatísticas da Documentação

- **Total de Documentos**: 40+
- **Guias de Setup**: 5
- **Guias Técnicos**: 8
- **Relatórios**: 7
- **Scripts**: 15+
- **Testes**: 10+
- **Última Atualização**: Outubro 2025

---

## 🔗 Links Importantes

### URLs do Sistema

- **API Local**: http://localhost:7777
- **Documentação**: http://localhost:7777/docs
- **Health Check**: http://localhost:7777/healthz
- **Control Plane**: https://platform.agno.com

### Documentação Externa

- **Agno Docs**: https://docs.agno.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **OpenAI API**: https://platform.openai.com/docs
- **Supabase Docs**: https://supabase.com/docs

### Repositórios

- **Agno Framework**: https://github.com/agno-agi/agno
- **GitLab (Projeto)**: (configurar conforme seu repo)

---

## 📝 Notas

### Documentos Essenciais ⭐

Os documentos marcados com ⭐ são os mais importantes para começar:

1. [RELATORIO_ANALISE_COMPLETA_ARIA.md](RELATORIO_ANALISE_COMPLETA_ARIA.md)
2. [GUIA_AGNO_FRAMEWORK.md](GUIA_AGNO_FRAMEWORK.md)
3. [CHECKLIST_PRODUCAO.md](CHECKLIST_PRODUCAO.md)

### Ordem de Leitura Recomendada

**Para Desenvolvedores Novos**:
1. COMECE_AQUI.txt
2. INICIO_RAPIDO.md
3. README.md
4. GUIA_AGNO_FRAMEWORK.md
5. RELATORIO_ANALISE_COMPLETA_ARIA.md

**Para DevOps**:
1. CHECKLIST_PRODUCAO.md
2. README_DEPLOY.md
3. DEPLOY_OPTIONS.md
4. docker-compose.yml
5. GITLAB_SETUP.md

**Para Arquitetos**:
1. RELATORIO_ANALISE_COMPLETA_ARIA.md
2. docs/ARCHITECTURE.md
3. RELATORIO_TECNICO_MIGRACAO_ARIA.md
4. GUIA_AGNO_FRAMEWORK.md
5. docs/AGNO_OPTIMIZATION_PLAN.md

---

## 🆘 Precisa de Ajuda?

1. **Primeiro passo**: Busque neste índice o tópico relacionado
2. **Problemas técnicos**: Veja seção Troubleshooting em [TESTE_LOCAL_GUIA.md](TESTE_LOCAL_GUIA.md)
3. **Erros de webhook**: Consulte [SOLUCAO_WEBHOOK_404.md](SOLUCAO_WEBHOOK_404.md)
4. **Dúvidas sobre Agno**: Leia [GUIA_AGNO_FRAMEWORK.md](GUIA_AGNO_FRAMEWORK.md)
5. **Deploy**: Siga [CHECKLIST_PRODUCAO.md](CHECKLIST_PRODUCAO.md)

---

**Última atualização**: Outubro 2025  
**Versão**: 1.0  
**Projeto**: ARIA-SDR  
**Mantenedor**: Equipe AR Online

