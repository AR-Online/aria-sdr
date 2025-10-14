# Contributing to ARIA-SDR

Thank you for your interest in contributing to ARIA-SDR! This document provides guidelines for contributing to the project.

## Code of Conduct

This project follows the AR Online Code of Conduct. By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.10+ (recomendado 3.11)
- Git
- Docker (opcional)
- GitLab account

### Development Setup

1. **Fork e Clone**

   ```bash
   git clone https://gitlab.com/seu-usuario/aria-sdr.git
   cd aria-sdr
   ```

2. **Ambiente Virtual**

   ```bash
   python -m venv agno_env
   agno_env\Scripts\activate  # Windows
   # ou
   source agno_env/bin/activate  # Linux/Mac
   ```

3. **Dependencias**

   ```bash
   pip install 'openai<1.100.0'  # Versao compativel
   pip install agno fastapi uvicorn
   pip install -r requirements-dev.txt
   ```

4. **Configuracao**

   ```bash
   cp config.env.example .env
   # Editar .env com suas credenciais
   ```

## Development Workflow

### Branch Strategy

- `main`: Branch principal (produção)
- `develop`: Branch de desenvolvimento
- `feature/*`: Novas funcionalidades
- `fix/*`: Correções de bugs
- `hotfix/*`: Correções urgentes

### Commit Messages

Use o formato convencional:

```
type(scope): descrição

Corpo da mensagem (opcional)

Footer (opcional)
```

Tipos aceitos:
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Tarefas de manutenção

### Pull Request Process

1. **Criar Branch**

   ```bash
   git checkout -b feature/nova-funcionalidade
   ```

2. **Desenvolver**
   - Escrever código
   - Adicionar testes
   - Atualizar documentação

3. **Testes Locais**

   ```bash
   ruff check .
   ruff format .
   pytest tests/ -v
   ```

4. **Commit**

   ```bash
   git add .
   git commit -m "feat: adiciona nova funcionalidade"
   ```

5. **Push e PR**

   ```bash
   git push origin feature/nova-funcionalidade
   # Criar Pull Request no GitLab
   ```

## Code Standards

### Python

- **Style**: PEP 8
- **Linting**: Ruff
- **Formatting**: Ruff format
- **Type Hints**: Recomendado
- **Docstrings**: Google style

### GitLab CI/CD

- **Pipeline**: Deve passar todos os testes
- **Linting**: Ruff check e format
- **Security**: Safety e Bandit
- **Coverage**: Manter cobertura de testes

### Documentation

- **README**: Manter atualizado
- **Docstrings**: Para todas as funções públicas
- **Changelog**: Documentar mudanças
- **Comments**: Código complexo deve ter comentários

## Testing

### Executar Testes

```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/test_smoke_api.py -v

# Com cobertura
pytest --cov=main --cov-report=html
```

### Tipos de Teste

- **Unit Tests**: Funções individuais
- **Integration Tests**: Integrações entre componentes
- **API Tests**: Endpoints da API
- **WhatsApp Tests**: Integração WhatsApp

## Environment Variables

### Desenvolvimento

```bash
# OpenAI
OPENAI_API_KEY=sk-...
ASSISTANT_ID=asst-...

# Supabase
SUPABASE_URL=https://...
SUPABASE_SERVICE_ROLE_KEY=...

# Mindchat
MINDCHAT_API_TOKEN=...
MINDCHAT_API_BASE_URL=https://...

# FastAPI
FASTAPI_BEARER_TOKEN=dtransforma2026
```

### Produção

- Usar GitLab CI/CD Variables
- Nunca commitar credenciais
- Usar tokens com escopo mínimo

## Troubleshooting

### Problemas Comuns

1. **OpenAI Dependency Error**

   ```bash
   pip uninstall openai -y
   pip install openai==1.99.9
   ```

2. **AgentOS não inicia**

   ```bash
   agno_env\Scripts\activate
   python -c "import openai; print(openai.__version__)"
   ```

3. **Pipeline falha**

   ```bash
   ruff check .
   ruff format .
   ```

## Release Process

### Versioning

Seguir [Semantic Versioning](https://semver.org/):
- `MAJOR`: Mudanças incompatíveis
- `MINOR`: Nova funcionalidade compatível
- `PATCH`: Correções compatíveis

### Release Steps

1. **Atualizar CHANGELOG.md**
2. **Criar tag**

   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

3. **Deploy automático via GitLab CI/CD**

## Support

### Getting Help

- **Issues**: [GitLab Issues](https://gitlab.com/lourealiza/aria-sdr/-/issues)
- **Email**: suporte@ar-online.com.br
- **Documentation**: [docs.agno.com](https://docs.agno.com)

### Reporting Bugs

1. Verificar se já existe issue
2. Usar template de bug report
3. Incluir logs e steps para reproduzir
4. Adicionar labels apropriados

### Feature Requests

1. Verificar se já existe request
2. Usar template de feature request
3. Descrever caso de uso
4. Adicionar labels apropriados

## License

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para detalhes.

---

**ARIA-SDR** - Contribuindo para o futuro da IA conversacional 🤖✨
