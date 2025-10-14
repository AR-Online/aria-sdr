# CI/CD Inputs - Guia de Uso para ARIA-SDR

## 🚀 Visão Geral

Este projeto implementa **CI/CD Inputs** do GitLab conforme a [documentação oficial](https://docs.gitlab.com/ci/inputs/#define-input-parameters-with-specinputs) para tornar os pipelines mais flexíveis e reutilizáveis.

## 📋 Inputs Disponíveis

### Pipeline Principal (`.gitlab-ci.yml`)

| Input | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `python_version` | string | "3.11" | Versão do Python (3.10, 3.11, 3.12) |
| `test_stage` | string | "test" | Stage para executar testes |
| `deploy_environment` | string | "staging" | Ambiente de deploy (staging, production) |
| `run_security_scan` | boolean | true | Executar análise de segurança |
| `run_docs_check` | boolean | true | Verificar documentação |
| `parallel_builds` | number | 3 | Número de builds paralelos |
| `cache_expiry` | number | 24 | Tempo de expiração do cache (horas) |

### Template Reutilizável (`.gitlab-ci-template.yml`)

| Input | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `project_name` | string | "aria-sdr" | Nome do projeto |
| `python_version` | string | "3.11" | Versão do Python |
| `test_command` | string | "pytest tests/ -v" | Comando de teste personalizado |
| `build_command` | string | "python -c 'import main; print(\"Build OK\")'" | Comando de build personalizado |
| `deploy_url` | string | "https://api.ar-online.com.br" | URL de deploy |
| `enable_security` | boolean | true | Habilitar análise de segurança |
| `enable_docs` | boolean | true | Habilitar verificação de documentação |

## 🎯 Como Usar

### 1. Pipeline Manual com Inputs

Para executar um pipeline manual com inputs personalizados:

```bash
# Via GitLab UI
1. Vá para CI/CD > Pipelines
2. Clique em "Run pipeline"
3. Configure os inputs desejados
4. Execute o pipeline
```

### 2. Usando o Template

Para usar o template em outro projeto:

```yaml
# .gitlab-ci.yml do projeto
include:
  - local: '.gitlab-ci-template.yml'
    inputs:
      project_name: 'meu-projeto'
      python_version: '3.12'
      test_command: 'pytest tests/ -v --cov'
      deploy_url: 'https://meu-projeto.com'
```

### 3. Pipeline com Inputs via API

```bash
curl -X POST \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ref": "main",
    "inputs": {
      "python_version": "3.12",
      "deploy_environment": "production",
      "run_security_scan": true
    }
  }' \
  "https://gitlab.com/api/v4/projects/$PROJECT_ID/pipeline"
```

## 🔧 Exemplos Práticos

### Exemplo 1: Pipeline de Desenvolvimento

```yaml
# Inputs para desenvolvimento
inputs:
  python_version: "3.11"
  deploy_environment: "staging"
  run_security_scan: true
  run_docs_check: true
```

### Exemplo 2: Pipeline de Produção

```yaml
# Inputs para produção
inputs:
  python_version: "3.12"
  deploy_environment: "production"
  run_security_scan: true
  run_docs_check: false
```

### Exemplo 3: Pipeline de Teste Rápido

```yaml
# Inputs para teste rápido
inputs:
  python_version: "3.11"
  run_security_scan: false
  run_docs_check: false
  parallel_builds: 1
```

## 🛠️ Funções de Interpolação

### Função `expand_vars`

Expande variáveis CI/CD nos inputs:

```yaml
spec:
  inputs:
    branch:
      default: '$CI_DEFAULT_BRANCH'
---
job:
  script: echo $[[ inputs.branch | expand_vars ]]
```

### Função `truncate`

Trunca valores de input:

```yaml
spec:
  inputs:
    long_text:
      default: 'Este é um texto muito longo'
---
job:
  script: echo $[[ inputs.long_text | truncate(0,10) ]]
```

## 🚨 Troubleshooting

### Problema: Pipeline falha com inputs obrigatórios

**Solução**: Sempre defina valores padrão para inputs:

```yaml
spec:
  inputs:
    required_input:
      default: "valor-padrao"  # Sempre definir padrão
```

### Problema: Input não é reconhecido

**Solução**: Verificar sintaxe do input:

```yaml
# Correto
$[[ inputs.input_name ]]

# Incorreto
$[[ input.input_name ]]  # Falta o 's'
```

### Problema: Input com aspas em rules

**Solução**: Usar aspas adequadas:

```yaml
rules:
  - if: '"$[[ inputs.environment ]]" == "production"'
```

## 📚 Referências

- [GitLab CI/CD Inputs Documentation](https://docs.gitlab.com/ci/inputs/#define-input-parameters-with-specinputs)
- [GitLab CI/CD Variables](https://docs.gitlab.com/ee/ci/variables/)
- [GitLab Pipeline Triggers](https://docs.gitlab.com/ee/ci/triggers/)

## 🎯 Benefícios dos Inputs

1. **✅ Flexibilidade**: Pipelines parametrizáveis
2. **✅ Reutilização**: Templates reutilizáveis
3. **✅ Validação**: Validação automática de tipos
4. **✅ Documentação**: Descrições claras dos parâmetros
5. **✅ Manutenibilidade**: Configuração centralizada
6. **✅ Segurança**: Validação de entrada robusta

---

**ARIA-SDR** - Pipelines inteligentes com CI/CD Inputs 🤖✨
