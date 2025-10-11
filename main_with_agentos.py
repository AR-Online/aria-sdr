# main_with_agentos.py - IntegraÃ§Ã£o AgentOS com servidor existente
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import secrets
import time
from datetime import datetime, timezone
from typing import Any

import requests
from dotenv import find_dotenv, load_dotenv
from fastapi import Body, Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load .env
load_dotenv(find_dotenv(), override=False)
DEBUG = (os.getenv("API_DEBUG", "false") or "").lower() == "true"

# Create FastAPI app
app = FastAPI(title="ARIA-SDR com AgentOS", debug=DEBUG)

API_TOKEN = (os.getenv("FASTAPI_BEARER_TOKEN") or "").strip()
auth_scheme = HTTPBearer(auto_error=False)
log = logging.getLogger(__name__)

# Configuration
AGNO_AUTH_TOKEN = os.getenv("AGNO_AUTH_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Try to import AgentOS (optional)
try:
    from agno.agent import Agent
    from agno.os import AgentOS
    AGENTOS_AVAILABLE = True
    print("âœ… AgentOS disponÃ­vel")
except ImportError as e:
    AGENTOS_AVAILABLE = False
    print(f"âš ï¸ AgentOS nÃ£o disponÃ­vel: {e}")

# Create AgentOS if available
if AGENTOS_AVAILABLE:
    try:
        # Create a simple agent without OpenAI model to avoid compatibility issues
        aria_agent = Agent(
            name="ARIA-SDR",
            instructions="""
            VocÃª Ã© a ARIA, Agente de Relacionamento Inteligente da AR Online.
            
            Suas responsabilidades:
            1. Atender clientes via WhatsApp e chat web
            2. Classificar volumetria de envios (alto/baixo volume)
            3. Roteamento inteligente para FAQ, agendamento ou loja
            4. Responder em portuguÃªs brasileiro de forma cordial e objetiva
            
            Regras de negÃ³cio:
            - Volume alto: >= 1200 mensagens/mÃªs â†’ Agendamento
            - Volume baixo: < 1200 mensagens/mÃªs â†’ Loja
            - Use contexto fornecido quando disponÃ­vel
            - Se nÃ£o souber algo, ofereÃ§a encaminhar ao time
            """,
        )
        
        # Setup AgentOS
        agent_os = AgentOS(
            description="ARIA-SDR - Agente de Relacionamento Inteligente da AR Online",
            agents=[aria_agent],
        )
        
        # Get AgentOS routes
        agentos_routes = agent_os.get_routes()
        print(f"âœ… AgentOS configurado com {len(agentos_routes)} rotas")
        
        # Add AgentOS routes to our app
        for route in agentos_routes:
            app.router.routes.append(route)
            print(f"âž• Rota adicionada: {route.path}")
            
    except Exception as e:
        print(f"âŒ Erro ao configurar AgentOS: {e}")
        AGENTOS_AVAILABLE = False

# Custom routes for ARIA-SDR
@app.get("/healthz")
def healthz():
    return {
        "ok": True, 
        "agentos": AGENTOS_AVAILABLE,
        "aria_agent": aria_agent.name if AGENTOS_AVAILABLE else None
    }

@app.post("/assist/routing")
def assist_routing(
    request: Request,
    payload: dict = Body(default_factory=dict),
    _tok: str = Depends(lambda cred: require_auth(cred) if cred else "no_auth"),
):
    """Endpoint principal de roteamento"""
    t0 = time.time()
    
    try:
        # Extract user input
        user_text = str(
            (payload or {}).get("input")
            or (payload or {}).get("user_text")
            or (payload or {}).get("message")
            or ""
        ).strip()
        
        v_in: dict[str, Any] = dict((payload or {}).get("variables") or {})
        
        # Generate thread ID
        app_thread_id = f"thr_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(2)}"
        
        # Use AgentOS if available
        if AGENTOS_AVAILABLE:
            try:
                response = aria_agent.run(user_text)
                reply_text = response.content if hasattr(response, 'content') else str(response)
                agent_used = True
            except Exception as e:
                log.error(f"AgentOS error: {e}")
                reply_text = "Desculpe, ocorreu um erro ao processar sua mensagem."
                agent_used = False
        else:
            # Fallback to original logic
            reply_text = "Sistema funcionando sem AgentOS."
            agent_used = False
        
        # Classify route
        route, vars_out, next_action = classify_route(user_text, v_in)
        
        # Log the interaction
        dur_ms = int((time.time() - t0) * 1000)
        log.info(f"ARIA routing: {app_thread_id} - {dur_ms}ms - AgentOS: {agent_used}")
        
        return {
            "reply_text": reply_text,
            "route": route,
            "thread_id": app_thread_id,
            "variables": vars_out or None,
            "next_action": next_action,
            "agentos": AGENTOS_AVAILABLE,
            "agent_used": agent_used,
        }
        
    except Exception as e:
        log.error(f"Routing error: {e}")
        return {"reply_text": "Erro interno do sistema.", "error": str(e)}

def classify_route(user_text: str, v: dict[str, Any]) -> tuple[str | None, dict[str, str], str | None]:
    """Classify route and volume deterministically"""
    t = (user_text or "").lower()
    route: str | None = None
    vars_out: dict[str, str] = {}
    next_action: str | None = None

    fp = str(v.get("fluxo_path") or "").strip().lower()
    if fp in {"envio", "recebimento"}:
        route = fp
    else:
        if any(k in t for k in ["recebi", "receb", "chegou", "abriu", "abertura", "confirmacao de leitura"]):
            route = "recebimento"
        elif any(k in t for k in ["enviar", "envio", "mandar", "disparar", "disparo", "quero enviar"]):
            route = "envio"

    if route == "envio":
        def classificar_volume(qtd: int) -> tuple[str, bool]:
            return ("alto", True) if qtd >= 1200 else ("baixo", False)

        vol_src = str(v.get("lead_volumetria", v.get("lead_duvida", ""))).lower()
        n: int | None = None
        m = re.findall(r"\d{1,3}(?:[\.,]\d{3})+|\d+", vol_src)
        if m:
            digits = re.sub(r"[^\d]", "", m[-1])
            if digits:
                n = int(digits)

        kw_high = re.search(r"(alto volume|grande volume|massivo|lote|mil|1k|1000\+|acima de|>\s*1000)", vol_src)

        if n is not None:
            vol_class, is_high = classificar_volume(n)
        else:
            is_high = bool(kw_high)
            vol_class = "alto" if is_high else "baixo"

        vars_out.update({
            "volume_num": str(n or ""),
            "lead_volumetria": str(n or vol_src or ""),
            "volume_alto": "true" if is_high else "false",
            "volume_class": vol_class,
        })
        next_action = "schedule" if is_high else "buy_credits"

    return route, vars_out, next_action

def require_auth(cred: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> str:
    if not cred:
        raise HTTPException(401, "Missing Authorization header")
    token = (cred.credentials or "").strip()
    if token != API_TOKEN:
        raise HTTPException(401, "Invalid token")
    return token

@app.get("/agentos/routes")
def get_agentos_routes():
    """List all AgentOS routes"""
    if not AGENTOS_AVAILABLE:
        return {"error": "AgentOS nÃ£o disponÃ­vel"}
    
    routes_info = []
    for route in agentos_routes:
        routes_info.append({
            "path": route.path,
            "name": route.name,
            "methods": getattr(route, 'methods', []),
        })
    
    return {
        "total_routes": len(routes_info),
        "routes": routes_info,
        "agentos_available": AGENTOS_AVAILABLE
    }

if __name__ == "__main__":
    """Run ARIA-SDR with AgentOS integration"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
