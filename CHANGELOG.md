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

### Changed
- Migracao completa de n8n para Agno Framework
- Atualizacao de dependencias OpenAI para versao compativel
- Melhoria na configuracao de ambiente virtual

### Fixed
- Erros de linting Ruff nos arquivos de teste
- Problemas de caracteres especiais no pipeline GitLab
- Conflitos de dependencias OpenAI com Agno
- Scripts de startup nao reconhecidos no PowerShell

### Security
- Implementacao de analise de seguranca com Safety e Bandit
- Validacao de dependencias em pipeline CI/CD

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
