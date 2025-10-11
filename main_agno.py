# main_agno.py - ARIA-SDR com AgentOS
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

# Agno AgentOS imports
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.tools.duckduckgo import DuckDuckGoTools

# Load .env without overriding existing process env (CI-friendly)
load_dotenv(find_dotenv(), override=False)
DEBUG = (os.getenv("API_DEBUG", "false") or "").lower() == "true"

# Create custom FastAPI app
app = FastAPI(title="ARIA-SDR AgentOS", debug=DEBUG)

API_TOKEN = (os.getenv("FASTAPI_BEARER_TOKEN") or "").strip()
auth_scheme = HTTPBearer(auto_error=False)
log = logging.getLogger(__name__)

# Configuration
AGNO_AUTH_TOKEN = os.getenv("AGNO_AUTH_TOKEN", "")
AGNO_BOT_ID = os.getenv("AGNO_BOT_ID", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1536"))

# Setup database for AgentOS
db = SqliteDb(db_file="tmp/aria_agentos.db")

# Create ARIA Agent with OpenAI
aria_agent = Agent(
    name="ARIA-SDR",
    model=OpenAIChat(id="gpt-4o-mini"),
    db=db,
    tools=[DuckDuckGoTools()],
    add_history_to_context=True,
    num_history_runs=5,
    add_datetime_to_context=True,
    markdown=True,
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

# Custom routes for ARIA-SDR
@app.get("/healthz")
def healthz():
    return {"ok": True, "agentos": True}

@app.post("/assist/routing")
def assist_routing(
    request: Request,
    payload: dict = Body(default_factory=dict),
    _tok: str = Depends(lambda cred: require_auth(cred) if cred else "no_auth"),
):
    """Endpoint principal de roteamento integrado com AgentOS"""
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
        x_thread_id = (request.headers.get("x-thread-id") or "").strip()
        body_thread_id = str((payload or {}).get("thread_id") or "").strip()
        
        def ensure_thread_id(remetente: str, canal: str) -> str:
            base = f"{canal}:{remetente}".strip().lower()
            return "thrd_" + hashlib.sha256(base.encode()).hexdigest()[:24]
        
        app_thread_id = x_thread_id or body_thread_id
        if not app_thread_id:
            remetente = str(v_in.get("remetente") or "").strip()
            canal = str(v_in.get("canal") or "").strip()
            if remetente and canal:
                app_thread_id = ensure_thread_id(remetente, canal)
            else:
                app_thread_id = (
                    f"thr_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(2)}"
                )
        
        # Use ARIA Agent to process the message
        try:
            response = aria_agent.run(user_text)
            reply_text = response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            log.error(f"Agent error: {e}")
            reply_text = "Desculpe, ocorreu um erro ao processar sua mensagem."
        
        # Classify volume if it's an "envio" request
        route, vars_out, next_action = classify_route(user_text, v_in)
        
        # Log the interaction
        dur_ms = int((time.time() - t0) * 1000)
        log.info(
            json.dumps(
                {
                    "level": "INFO",
                    "event": "routing_agentos",
                    "thread_id": app_thread_id,
                    "dur_ms": dur_ms,
                    "agent_used": True,
                },
                ensure_ascii=False,
            )
        )
        
        return {
            "reply_text": reply_text,
            "route": route,
            "thread_id": app_thread_id,
            "variables": vars_out or None,
            "next_action": next_action,
            "agentos": True,
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

# Setup AgentOS with our custom app
agent_os = AgentOS(
    description="ARIA-SDR - Agente de Relacionamento Inteligente da AR Online",
    agents=[aria_agent],
    base_app=app,
)

# Get the combined app with both AgentOS and our custom routes
app = agent_os.get_app()

if __name__ == "__main__":
    """Run ARIA-SDR with AgentOS"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
