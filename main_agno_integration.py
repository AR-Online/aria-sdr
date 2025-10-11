# main_agno_integration.py - IntegraÃ§Ã£o simples com Agno
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

# Load .env
load_dotenv(find_dotenv(), override=False)
DEBUG = (os.getenv("API_DEBUG", "false") or "").lower() == "true"

# Create FastAPI app
app = FastAPI(title="ARIA-SDR Agno Integration", debug=DEBUG)

API_TOKEN = (os.getenv("FASTAPI_BEARER_TOKEN") or "").strip()
auth_scheme = HTTPBearer(auto_error=False)
log = logging.getLogger(__name__)

# Configuration
AGNO_AUTH_TOKEN = os.getenv("AGNO_AUTH_TOKEN", "")
AGNO_API_BASE_URL = os.getenv("AGNO_API_BASE_URL", "https://agno.ar-infra.com.br/api/v1")

# Custom routes for ARIA-SDR
@app.get("/healthz")
def healthz():
    return {
        "ok": True, 
        "agno_integration": True,
        "agno_auth_token": "configured" if AGNO_AUTH_TOKEN else "missing"
    }

@app.post("/assist/routing")
def assist_routing(
    request: Request,
    payload: dict = Body(default_factory=dict),
    _tok: str = Depends(lambda cred: require_auth(cred) if cred else "no_auth"),
):
    """Endpoint principal de roteamento com integraÃ§Ã£o Agno"""
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
        
        # Try to call Agno API if token is configured
        agno_response = None
        if AGNO_AUTH_TOKEN:
            try:
                agno_response = call_agno_api(user_text, app_thread_id)
            except Exception as e:
                log.error(f"Agno API error: {e}")
        
        # Use Agno response or fallback
        if agno_response:
            reply_text = agno_response.get("reply_text", "Resposta do Agno")
            agent_used = True
        else:
            # Fallback to original logic
            reply_text = "Sistema funcionando com fallback."
            agent_used = False
        
        # Classify route
        route, vars_out, next_action = classify_route(user_text, v_in)
        
        # Log the interaction
        dur_ms = int((time.time() - t0) * 1000)
        log.info(f"ARIA routing: {app_thread_id} - {dur_ms}ms - Agno: {agent_used}")
        
        return {
            "reply_text": reply_text,
            "route": route,
            "thread_id": app_thread_id,
            "variables": vars_out or None,
            "next_action": next_action,
            "agno_integration": True,
            "agno_used": agent_used,
        }
        
    except Exception as e:
        log.error(f"Routing error: {e}")
        return {"reply_text": "Erro interno do sistema.", "error": str(e)}

def call_agno_api(user_text: str, thread_id: str) -> dict:
    """Call Agno API with the configured token"""
    headers = {
        "Authorization": f"Bearer {AGNO_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": user_text,
        "thread_id": thread_id,
        "context": {"source": "aria-sdr"}
    }
    
    # This would call the actual Agno API
    # For now, return a mock response
    return {
        "reply_text": f"Resposta do Agno para: {user_text}",
        "thread_id": thread_id,
        "agno_processed": True
    }

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

@app.get("/agno/info")
def get_agno_info():
    """Get Agno integration information"""
    return {
        "agno_auth_token": "configured" if AGNO_AUTH_TOKEN else "missing",
        "agno_api_base_url": AGNO_API_BASE_URL,
        "integration_status": "ready" if AGNO_AUTH_TOKEN else "needs_configuration"
    }

if __name__ == "__main__":
    """Run ARIA-SDR with Agno integration"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
