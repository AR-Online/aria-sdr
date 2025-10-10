"""
Módulo de integração com Cloudflare API para ARIA-SDR
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CloudflareAPI:
    """Cliente para integração com Cloudflare API"""
    
    def __init__(self):
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        if not self.api_token:
            logger.warning("CLOUDFLARE_API_TOKEN não configurado")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Faz requisição para a API Cloudflare"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição Cloudflare: {e}")
            return {"success": False, "error": str(e)}
    
    def get_zone_id(self, domain: str) -> Optional[str]:
        """Obtém o Zone ID para um domínio"""
        response = self._make_request("GET", f"/zones?name={domain}")
        
        if response.get("success") and response.get("result"):
            return response["result"][0]["id"]
        
        logger.error(f"Zone ID não encontrado para {domain}")
        return None
    
    def setup_rate_limiting(self, zone_id: str, domain: str) -> Dict[str, Any]:
        """Configura rate limiting para proteger endpoints"""
        
        rate_limit_config = {
            "rules": [
                {
                    "targets": [
                        {
                            "target": "url",
                            "constraint": {
                                "operator": "matches",
                                "value": f"{domain}/assist/*"
                            }
                        }
                    ],
                    "actions": [
                        {
                            "id": "rate_limit",
                            "value": {
                                "requests_per_period": 1000,
                                "period": 60,
                                "action": "block"
                            }
                        }
                    ]
                }
            ]
        }
        
        return self._make_request(
            "POST", 
            f"/zones/{zone_id}/rulesets",
            json=rate_limit_config
        )
    
    def setup_bot_protection(self, zone_id: str) -> Dict[str, Any]:
        """Configura proteção contra bots"""
        
        bot_config = {
            "value": {
                "bot_fight_mode": True,
                "super_bot_fight_mode": True,
                "challenge_passage": 30
            }
        }
        
        return self._make_request(
            "PATCH",
            f"/zones/{zone_id}/settings/bot_fight_mode",
            json=bot_config
        )
    
    def create_health_check(self, zone_id: str, domain: str) -> Dict[str, Any]:
        """Cria health check para monitoramento"""
        
        health_check_config = {
            "name": "ARIA-SDR Health Check",
            "description": "Monitora saúde da API ARIA-SDR",
            "address": domain,
            "port": 443,
            "type": "HTTPS",
            "interval": 60,
            "retries": 3,
            "timeout": 5,
            "method": "GET",
            "path": "/healthz",
            "expected_codes": "200",
            "follow_redirects": True,
            "allow_insecure": False
        }
        
        return self._make_request(
            "POST",
            f"/zones/{zone_id}/healthchecks",
            json=health_check_config
        )
    
    def get_analytics(self, zone_id: str, days: int = 7) -> Dict[str, Any]:
        """Obtém analytics de tráfego"""
        
        since = (datetime.now() - timedelta(days=days)).isoformat()
        until = datetime.now().isoformat()
        
        params = {
            "since": since,
            "until": until,
            "dimensions": ["clientCountry", "clientDeviceType", "clientIPClass"],
            "metrics": ["requests", "bytes", "cachedRequests", "pageViews"]
        }
        
        return self._make_request(
            "GET",
            f"/zones/{zone_id}/analytics/dashboard",
            params=params
        )
    
    def get_security_events(self, zone_id: str, hours: int = 24) -> Dict[str, Any]:
        """Obtém eventos de segurança"""
        
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        until = datetime.now().isoformat()
        
        params = {
            "since": since,
            "until": until,
            "per_page": 100
        }
        
        return self._make_request(
            "GET",
            f"/zones/{zone_id}/security/events",
            params=params
        )
    
    def purge_cache(self, zone_id: str, urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """Limpa cache do Cloudflare"""
        
        if urls:
            purge_config = {"files": urls}
        else:
            purge_config = {"purge_everything": True}
        
        return self._make_request(
            "POST",
            f"/zones/{zone_id}/purge_cache",
            json=purge_config
        )
    
    def setup_dns_record(self, zone_id: str, name: str, content: str, 
                        record_type: str = "A", ttl: int = 300) -> Dict[str, Any]:
        """Cria registro DNS"""
        
        dns_config = {
            "type": record_type,
            "name": name,
            "content": content,
            "ttl": ttl,
            "proxied": True  # Ativa proxy do Cloudflare
        }
        
        return self._make_request(
            "POST",
            f"/zones/{zone_id}/dns_records",
            json=dns_config
        )


def setup_cloudflare_protection(domain: str = "api.ar-online.com.br") -> Dict[str, Any]:
    """Configura proteção completa do Cloudflare para ARIA-SDR"""
    
    cf = CloudflareAPI()
    
    if not cf.api_token:
        return {"success": False, "error": "Cloudflare API token não configurado"}
    
    # Obter Zone ID
    zone_id = cf.get_zone_id(domain)
    if not zone_id:
        return {"success": False, "error": f"Zone ID não encontrado para {domain}"}
    
    results = {}
    
    try:
        # Configurar Rate Limiting
        results["rate_limiting"] = cf.setup_rate_limiting(zone_id, domain)
        
        # Configurar Bot Protection
        results["bot_protection"] = cf.setup_bot_protection(zone_id)
        
        # Criar Health Check
        results["health_check"] = cf.create_health_check(zone_id, domain)
        
        logger.info(f"Proteção Cloudflare configurada para {domain}")
        return {"success": True, "zone_id": zone_id, "results": results}
        
    except Exception as e:
        logger.error(f"Erro ao configurar Cloudflare: {e}")
        return {"success": False, "error": str(e)}


def get_cloudflare_metrics(domain: str = "api.ar-online.com.br") -> Dict[str, Any]:
    """Obtém métricas do Cloudflare para ARIA-SDR"""
    
    cf = CloudflareAPI()
    
    if not cf.api_token:
        return {"success": False, "error": "Cloudflare API token não configurado"}
    
    zone_id = cf.get_zone_id(domain)
    if not zone_id:
        return {"success": False, "error": f"Zone ID não encontrado para {domain}"}
    
    try:
        # Obter analytics
        analytics = cf.get_analytics(zone_id, days=7)
        
        # Obter eventos de segurança
        security_events = cf.get_security_events(zone_id, hours=24)
        
        return {
            "success": True,
            "analytics": analytics,
            "security_events": security_events,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas Cloudflare: {e}")
        return {"success": False, "error": str(e)}
