# Integração Cloudflare - ARIA-SDR

## Visão Geral

O ARIA-SDR está integrado com a **Cloudflare API** para aproveitar os serviços de infraestrutura, segurança e performance da plataforma.

## Configuração Atual

```bash
# Token da API Cloudflare (já configurado)
CLOUDFLARE_API_TOKEN=JV_d0yng1HI5vcxJaebMpiuoC04gRifT3SbBhT7U
```

## Funcionalidades Disponíveis

### 🔒 **Segurança**
- **Bot Management** - Proteção contra bots maliciosos
- **Firewall** - Regras de firewall personalizadas
- **Rate Limiting** - Controle de taxa de requisições
- **DDoS Protection** - Proteção automática contra ataques

### 🌐 **DNS & Networking**
- **DNS Management** - Gestão de registros DNS
- **Load Balancing** - Distribuição de carga
- **Magic Transit** - Rede privada global
- **Health Checks** - Monitoramento de saúde dos serviços

### ⚡ **Performance**
- **Cache** - Cache inteligente de conteúdo
- **Argo** - Otimização de roteamento
- **Speed** - Análise de performance
- **Waiting Rooms** - Controle de tráfego

### 📊 **Analytics & Monitoring**
- **Analytics** - Métricas detalhadas
- **Logs** - Logs em tempo real
- **RUM** - Real User Monitoring
- **Radar** - Inteligência de tráfego

## Implementação no ARIA-SDR

### 1. Proteção de Endpoints

```python
import requests
import os

def protect_endpoint_with_cloudflare():
    """Protege endpoints do ARIA-SDR com Cloudflare"""
    
    CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
    ZONE_ID = "sua-zone-id"  # ID da zona Cloudflare
    
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Configurar Rate Limiting
    rate_limit_config = {
        "match": {
            "request": {
                "url": "api.ar-online.com.br/assist/*"
            }
        },
        "action": "rate_limit",
        "ratelimit": {
            "requests_per_period": 100,
            "period": 60
        }
    }
    
    response = requests.post(
        f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/rulesets",
        json=rate_limit_config,
        headers=headers
    )
    
    return response.json()
```

### 2. Monitoramento de Saúde

```python
def setup_health_monitoring():
    """Configura monitoramento de saúde com Cloudflare"""
    
    health_check_config = {
        "name": "ARIA-SDR Health Check",
        "description": "Monitora saúde da API ARIA-SDR",
        "address": "api.ar-online.com.br",
        "port": 443,
        "type": "HTTPS",
        "interval": 60,
        "retries": 3,
        "timeout": 5,
        "method": "GET",
        "path": "/healthz",
        "expected_codes": "200"
    }
    
    response = requests.post(
        f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/healthchecks",
        json=health_check_config,
        headers=headers
    )
    
    return response.json()
```

### 3. Analytics de Tráfego

```python
def get_traffic_analytics():
    """Obtém analytics de tráfego do ARIA-SDR"""
    
    analytics_params = {
        "since": "-7d",  # Últimos 7 dias
        "until": "now",
        "dimensions": ["clientCountry", "clientDeviceType"],
        "metrics": ["requests", "bytes", "cachedRequests"]
    }
    
    response = requests.get(
        f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/analytics/dashboard",
        params=analytics_params,
        headers=headers
    )
    
    return response.json()
```

### 4. Configuração de Cache

```python
def configure_cache_rules():
    """Configura regras de cache para otimizar performance"""
    
    cache_config = {
        "rules": [
            {
                "targets": [
                    {
                        "target": "url",
                        "constraint": {
                            "operator": "matches",
                            "value": "api.ar-online.com.br/static/*"
                        }
                    }
                ],
                "actions": [
                    {
                        "id": "cache_level",
                        "value": "cache_everything"
                    },
                    {
                        "id": "edge_ttl",
                        "value": {
                            "default": 86400  # 24 horas
                        }
                    }
                ]
            }
        ]
    }
    
    response = requests.post(
        f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/rulesets",
        json=cache_config,
        headers=headers
    )
    
    return response.json()
```

## Endpoints Úteis para ARIA-SDR

### Segurança
- `POST /zones/{zone_id}/rulesets` - Configurar regras de segurança
- `GET /zones/{zone_id}/security/events` - Eventos de segurança
- `POST /zones/{zone_id}/rate_limits` - Rate limiting

### DNS
- `GET /zones/{zone_id}/dns_records` - Listar registros DNS
- `POST /zones/{zone_id}/dns_records` - Criar registro DNS
- `PUT /zones/{zone_id}/dns_records/{record_id}` - Atualizar registro

### Analytics
- `GET /zones/{zone_id}/analytics/dashboard` - Dashboard de analytics
- `GET /zones/{zone_id}/analytics/colos` - Dados por colo
- `GET /zones/{zone_id}/logs/received` - Logs em tempo real

### Performance
- `GET /zones/{zone_id}/cache/purge` - Limpar cache
- `POST /zones/{zone_id}/cache/purge` - Purge seletivo
- `GET /zones/{zone_id}/speed` - Análise de velocidade

## Configuração Recomendada para ARIA-SDR

### 1. Rate Limiting
```json
{
  "requests_per_period": 1000,
  "period": 60,
  "action": "block"
}
```

### 2. Bot Protection
```json
{
  "bot_fight_mode": true,
  "super_bot_fight_mode": true,
  "challenge_passage": 30
}
```

### 3. Cache Rules
```json
{
  "static_content": "cache_everything",
  "api_endpoints": "bypass_cache",
  "ttl": 3600
}
```

## Monitoramento e Alertas

### Métricas Importantes
- **Requests per second** - Volume de requisições
- **Error rate** - Taxa de erro
- **Response time** - Tempo de resposta
- **Cache hit ratio** - Eficiência do cache

### Alertas Recomendados
- Taxa de erro > 5%
- Tempo de resposta > 2s
- Volume de requisições > 10k/min
- Ataques DDoS detectados

## Documentação Oficial

Para mais detalhes sobre a Cloudflare API, consulte:
**[https://developers.cloudflare.com/api/](https://developers.cloudflare.com/api/)**

## Próximos Passos

1. **Configurar Zone ID** da AR Online
2. **Implementar Rate Limiting** para endpoints críticos
3. **Configurar Health Checks** para monitoramento
4. **Ativar Bot Protection** para segurança
5. **Implementar Analytics** para métricas
