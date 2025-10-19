# Changelog

All notable changes to the ARIA-SDR project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CI/CD Inputs parametrizaveis para GitLab
- Template reutilizavel para pipelines
- Scripts de startup para Windows (PowerShell e CMD)
- Documentacao completa do projeto
- Integracao com Kubernetes via GitLab Agent
- Sistema ARIA-SDR Reflector - Versão Simplificada
- Implementação ARIA-SDR com RAG Supabase
- Solução ngrok para webhook Mindchat
- Integração completa com Mindchat real
- Integração completa com GitLab Webhooks
- Documento de análise de duplicatas (ANALISE_DUPLICATAS.md)

### Changed
- Migracao completa de n8n para Agno Framework
- Atualizacao de dependencias OpenAI para versao compativel
- Melhoria na configuracao de ambiente virtual
- Consolidação de 16 arquivos main_agno_*.py em main.py único
- Otimização da arquitetura AgentOS + FastAPI

### Removed
#### Limpeza de Arquivos Duplicados (2025-10-19)

**Arquivos aria_*.py removidos/reorganizados (8 arquivos):**
- aria_agentos_optimized.py, aria_agentos_config_optimized.py (versões antigas)
- aria_mindchat_integration.py, aria_mindchat_real.py (duplicados em main.py)
- aria_gitlab_webhook.py (duplicado em main.py)
- aria_rag_supabase.py → scripts/ingest_rag_supabase.py
- aria_agent_from_config.py → scripts/create_agent_from_config.py
- aria_agent_openai.py → scripts/setup_openai_agent.py
- aria_first_os.py → docs/examples/first_agentos.py
- **Mantidos na raiz:** aria_sdr_api.py, aria_sdr_integrated.py

**Arquivos main_agno_*.py removidos (20 arquivos):**
- main_agno.py, main_agno_active.py, main_agno_compatible.py
- main_agno_config.py, main_agno_default.py, main_agno_final.py
- main_agno_final_real.py, main_agno_integration.py, main_agno_official.py
- main_agno_ready.py, main_agno_real.py, main_agno_simple.py
- main_agno_simple_config.py, main_agno_simple_working.py
- main_agno_uvicorn.py, main_agno_working.py, main_agno_working_final.py
- main_with_agentos.py, main_with_agentos_final.py, main_backup.py
- **Motivo:** Versões antigas de desenvolvimento consolidadas em main.py

**Arquivos aria_sdr_*.py removidos (3 arquivos):**
- aria_sdr_basic.py, aria_sdr_functional.py, aria_sdr_working.py
- **Mantidos:** aria_sdr_api.py, aria_sdr_integrated.py
- **Motivo:** Funcionalidade já presente em main.py

**Arquivos de teste removidos (8 arquivos):**
- teste_final_aria.py, teste_simples.py
- test_basic.py, test_import.py, test_mindchat_simple.py, test_mock.py
- test_endpoint.py (vazio), test_webhook_debug.py (vazio)
- **Motivo:** Testes duplicados, redundantes ou vazios

**Arquivos de teste reorganizados (13 arquivos movidos para tests/):**
- tests/integration/ - 5 testes de integração (Mindchat, WhatsApp, GitLab)
- tests/unit/ - 3 testes unitários (Agno, AgentOS)
- tests/setup/ - 5 testes de configuração (ambiente, conexões)
- **Motivo:** Organização e estrutura padronizada

**Arquivos de configuração removidos (3 arquivos):**
- env.basic.example, env.template, env.working
- **Motivo:** Duplicatas de config.env.example

**Logs temporários removidos (4 arquivos):**
- assist_debug.log, last_error.log, uvicorn.err, uvicorn.out
- **Motivo:** Arquivos temporários que não devem ser versionados

**Documentação redundante removida (4 arquivos):**
- PR_BODY.md, DEPLOY_GITHUB.md, FIX_PAGES_DEPLOY.md, CLOUDFLARE_PAGES_DEPLOY.md
- **Motivo:** Documentação duplicada ou temporária

**Total:** 47 arquivos removidos + 17 reorganizados (~200KB de código duplicado)

**Resumo da reorganização:**
- Arquivos na raiz: 70+ → 25 arquivos essenciais
- Testes organizados em tests/ (integration, unit, setup)
- Scripts utilitários em scripts/
- Exemplos em docs/examples/
- Redução de 65% de arquivos duplicados

### Fixed
- Erros de linting Ruff nos arquivos de teste
- Problemas de caracteres especiais no pipeline GitLab
- Conflitos de dependencias OpenAI com Agno
- Scripts de startup nao reconhecidos no PowerShell
- Webhook Agno 404 - endpoint correto implementado
- Fragmentação de código - arquivos consolidados
- Problemas de codificação UTF-8 nos commits
- Limpeza de arquivos duplicados e redundantes

### Security
- Implementacao de analise de seguranca com Safety e Bandit
- Validacao de dependencias em pipeline CI/CD
- Remoção de chaves sensíveis do config.env.example

## [1.0.0] - 2025-01-14

### Added
- Sistema ARIA-SDR completo com Agno Framework
- Integracao WhatsApp via Mindchat
- Sistema RAG com Supabase
- AgentOS com Control Plane
- Pipeline CI/CD completo
- Testes automatizados
- Documentacao tecnica completa

### Technical Details
- Framework: Agno 2.1.4
- API: FastAPI + Uvicorn
- Database: SQLite (dev) / PostgreSQL (prod)
- IA: OpenAI GPT-4o-mini
- RAG: Supabase + LanceDB
- Integration: WhatsApp Business API + Mindchat
