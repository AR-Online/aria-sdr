# ✅ Checklist de Produção - ARIA-SDR

Use este checklist para garantir que o sistema está pronto para produção.

---

## 🔐 Segurança

### Autenticação e Tokens

- [ ] **FASTAPI_BEARER_TOKEN** configurado com token forte (mínimo 32 caracteres)
  ```bash
  # Gerar token seguro
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- [ ] **OPENAI_API_KEY** protegida e não exposta em logs
- [ ] **SUPABASE_SERVICE_ROLE_KEY** protegida
- [ ] **MINDCHAT_API_TOKEN** protegido
- [ ] Todas as chaves secretas em variáveis de ambiente (nunca no código)

### API Security

- [ ] CORS configurado corretamente (não usar `*` em produção)
- [ ] Rate limiting implementado
- [ ] HTTPS/TLS habilitado
- [ ] Validação de entrada em todos os endpoints
- [ ] Headers de segurança configurados
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  from fastapi.middleware.trustedhost import TrustedHostMiddleware
  ```

---

## 🗄️ Banco de Dados

### PostgreSQL (Obrigatório em Produção)

- [ ] **PostgreSQL** configurado (substituir SQLite)
  ```bash
  DATABASE_URL=postgresql://user:pass@host:5432/dbname
  ```

- [ ] Backup automático configurado
- [ ] Connection pooling habilitado
- [ ] Índices criados nas colunas frequentemente consultadas
- [ ] Migrations rodadas
- [ ] Monitoramento de performance

### Supabase (RAG)

- [ ] **SUPABASE_URL** configurado
- [ ] **SUPABASE_SERVICE_ROLE_KEY** configurado
- [ ] Função `match_aria_chunks` criada
- [ ] Tabela `rag_chunks` populada
- [ ] Embeddings gerados
- [ ] RLS (Row Level Security) configurado se necessário

---

## ⚙️ Configurações

### Variáveis de Ambiente Obrigatórias

```bash
# Essenciais
- [ ] OPENAI_API_KEY=sk-proj-...
- [ ] FASTAPI_BEARER_TOKEN=<token_forte>
- [ ] DATABASE_URL=postgresql://...

# API
- [ ] APP_ENV=production
- [ ] API_DEBUG=false
- [ ] API_LOG_LEVEL=info
- [ ] PORT=8000
- [ ] HOST=0.0.0.0

# RAG
- [ ] RAG_ENABLE=true
- [ ] SUPABASE_URL=https://...
- [ ] SUPABASE_SERVICE_ROLE_KEY=...
- [ ] EMBEDDING_MODEL=text-embedding-3-small
- [ ] EMBEDDING_DIM=1536

# WhatsApp (se usar)
- [ ] MINDCHAT_API_TOKEN=...
- [ ] MINDCHAT_API_BASE_URL=...
- [ ] WHATSAPP_NUMBER=...
```

### Configurações de Performance

```bash
# OpenAI
- [ ] CHAT_MODEL=gpt-4o-mini
- [ ] ASSISTANT_TIMEOUT_SECONDS=30

# RAG
- [ ] RAG_ENDPOINT=<url_producao>
- [ ] RAG_DEFAULT_SOURCE=faq

# Business Rules
- [ ] VOLUME_ALTO_LIMIAR=1200
```

---

## 🧪 Testes

### Testes Automatizados

- [ ] Todos os testes unitários passando
  ```bash
  pytest tests/unit/ -v
  ```

- [ ] Todos os testes de integração passando
  ```bash
  pytest tests/integration/ -v
  ```

- [ ] Testes de smoke passando
  ```bash
  pytest tests/test_smoke_api.py -v
  ```

- [ ] Coverage acima de 80%
  ```bash
  pytest --cov=. --cov-report=html
  ```

### Testes Manuais

- [ ] Health check funcionando: `GET /healthz`
- [ ] Autenticação funcionando corretamente
- [ ] RAG retornando resultados relevantes
- [ ] Roteamento classificando corretamente
- [ ] Volumetria calculada corretamente
- [ ] WhatsApp webhook recebendo mensagens (se aplicável)
- [ ] GitLab webhook funcionando (se aplicável)

### Testes de Carga

- [ ] Teste de carga básico realizado
  ```bash
  # Usar locust ou similar
  locust -f tests/load/locustfile.py
  ```

- [ ] Performance aceitável (< 2s por request)
- [ ] Sistema estável sob carga
- [ ] Sem memory leaks

---

## 📊 Monitoramento

### Logging

- [ ] Logs estruturados (JSON)
- [ ] Níveis de log apropriados
- [ ] Rotação de logs configurada
- [ ] Logs agregados (CloudWatch, Datadog, etc.)

```python
import logging
import json

logger = logging.getLogger(__name__)
logger.info(json.dumps({
    "event": "request",
    "endpoint": "/assist/routing",
    "duration_ms": 150,
    "status": "success"
}))
```

### Métricas

- [ ] Tempo de resposta por endpoint
- [ ] Taxa de erros
- [ ] Uso de CPU e memória
- [ ] Conexões de banco de dados
- [ ] Rate de chamadas à OpenAI API
- [ ] Cache hit rate (se aplicável)

### Alertas

- [ ] Alerta de erro rate > 5%
- [ ] Alerta de latência > 3s
- [ ] Alerta de uso de memória > 80%
- [ ] Alerta de API quota OpenAI
- [ ] Alerta de downtime

### Health Checks

- [ ] Endpoint `/healthz` respondendo
- [ ] Verificação de conectividade com banco
- [ ] Verificação de conectividade com Supabase
- [ ] Verificação de conectividade com OpenAI

---

## 🚀 Deploy

### Infraestrutura

- [ ] Servidor/container provisionado
- [ ] Firewall configurado
- [ ] SSL/TLS certificado
- [ ] Domain/DNS configurado
- [ ] Load balancer (se necessário)

### Aplicação

- [ ] Código em repositório Git
- [ ] Build automatizado (CI/CD)
- [ ] Testes automáticos no CI/CD
- [ ] Deploy automatizado
- [ ] Rollback strategy definida
- [ ] Blue-green ou canary deployment

### Docker (se usar)

- [ ] Dockerfile otimizado
- [ ] Multi-stage build
- [ ] Imagem < 500MB
- [ ] Health check no container
- [ ] docker-compose.yml para produção

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📈 Performance

### Otimizações

- [ ] Connection pooling habilitado
- [ ] Cache implementado (Redis, Memcached)
- [ ] Embeddings cacheados
- [ ] Compressão de resposta (gzip)
- [ ] Static files servidos via CDN

### Limites

- [ ] Request timeout configurado (30s)
- [ ] Max request size configurado (10MB)
- [ ] Rate limiting por IP/user
- [ ] Connection limits

```python
from fastapi import Request
from fastapi.responses import JSONResponse
import time

@app.middleware("http")
async def add_timeout(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

---

## 🔄 Backup e Recuperação

### Backups

- [ ] Backup automático do banco de dados (diário)
- [ ] Backup de arquivos estáticos
- [ ] Backup de configurações
- [ ] Backup testado (restore funciona)
- [ ] Retention policy definida (30 dias)

### Disaster Recovery

- [ ] Plano de recuperação documentado
- [ ] RTO (Recovery Time Objective) definido
- [ ] RPO (Recovery Point Objective) definido
- [ ] Processo de restore testado
- [ ] Contatos de emergência

---

## 📝 Documentação

### Documentação Técnica

- [ ] README.md atualizado
- [ ] API documentada (Swagger/OpenAPI)
- [ ] Arquitetura documentada
- [ ] Fluxos de negócio documentados
- [ ] Guia de troubleshooting

### Documentação Operacional

- [ ] Runbook para operação
- [ ] Procedimentos de deploy
- [ ] Procedimentos de rollback
- [ ] Procedimentos de backup/restore
- [ ] Contatos e escalação

### Documentação de Código

- [ ] Docstrings em funções importantes
- [ ] Comentários explicativos onde necessário
- [ ] Type hints em funções
- [ ] CHANGELOG.md atualizado

---

## 👥 Equipe

### Conhecimento

- [ ] Pelo menos 2 pessoas conhecem o sistema
- [ ] Documentação de onboarding
- [ ] Sessões de knowledge transfer realizadas
- [ ] Code reviews obrigatórios

### Acesso

- [ ] Acesso ao servidor configurado
- [ ] Acesso ao banco de dados configurado
- [ ] Acesso aos logs configurado
- [ ] Acesso às métricas configurado
- [ ] Acesso de emergência documentado

---

## 🔍 Conformidade

### LGPD / GDPR (se aplicável)

- [ ] Dados pessoais identificados
- [ ] Política de privacidade definida
- [ ] Consentimento do usuário implementado
- [ ] Direito ao esquecimento implementado
- [ ] Logs de acesso a dados pessoais
- [ ] Criptografia de dados sensíveis

### Auditoria

- [ ] Logs de auditoria habilitados
- [ ] Ações administrativas logadas
- [ ] Acessos a dados sensíveis logados
- [ ] Retenção de logs configurada

---

## 🎯 Pré-Deploy Checklist

### 24 horas antes

- [ ] Avisar stakeholders
- [ ] Agendar janela de manutenção
- [ ] Fazer backup completo
- [ ] Revisar mudanças
- [ ] Preparar rollback

### 1 hora antes

- [ ] Verificar health checks
- [ ] Verificar métricas atuais
- [ ] Preparar monitoramento
- [ ] Equipe em standby

### Durante Deploy

- [ ] Executar migration de banco (se houver)
- [ ] Deploy da aplicação
- [ ] Verificar health checks
- [ ] Smoke tests
- [ ] Verificar logs

### Pós-Deploy

- [ ] Monitorar métricas (15 min)
- [ ] Verificar logs de erro
- [ ] Testar funcionalidades críticas
- [ ] Avisar stakeholders (sucesso)
- [ ] Atualizar documentação

---

## ⚠️ Red Flags (Não Deploy se...)

- ❌ Testes falhando
- ❌ Performance degradada
- ❌ Dependências desatualizadas com vulnerabilidades
- ❌ Configurações de produção não validadas
- ❌ Backup não funcionando
- ❌ Equipe não disponível para suporte
- ❌ Sexta-feira tarde ou véspera de feriado 😉

---

## ✅ Checklist de Validação Pós-Produção

### Primeira Hora

- [ ] Health check OK
- [ ] Logs sem erros críticos
- [ ] Métricas normais
- [ ] Testes de smoke passando

### Primeiro Dia

- [ ] Monitoramento ativo
- [ ] Alertas configurados
- [ ] Performance aceitável
- [ ] Usuários sem reclamações

### Primeira Semana

- [ ] Métricas coletadas e analisadas
- [ ] Nenhum incidente crítico
- [ ] Performance estável
- [ ] Feedback dos usuários positivo

---

## 📞 Contatos de Emergência

```
# Adicionar contatos reais
Equipe de Desenvolvimento: ...
DevOps: ...
DBA: ...
Gerente de Projeto: ...
Suporte OpenAI: support@openai.com
Suporte Supabase: support@supabase.io
```

---

## 🎓 Recursos Adicionais

- [Guia de Teste Local](TESTE_LOCAL_GUIA.md)
- [Guia Agno Framework](GUIA_AGNO_FRAMEWORK.md)
- [README Principal](README.md)
- [Relatório de Análise](RELATORIO_ANALISE_COMPLETA_ARIA.md)

---

**Última atualização**: Outubro 2025  
**Versão**: 1.0  
**Projeto**: ARIA-SDR

