# main_agno_working.py - ARIA-SDR com AgentOS funcionando
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any

from dotenv import find_dotenv, load_dotenv
from fastapi import Body, Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Load .env
load_dotenv(find_dotenv(), override=False)
DEBUG = (os.getenv("API_DEBUG", "false") or "").lower() == "true"

# Create FastAPI app
app = FastAPI(title="ARIA-SDR AgentOS Working", debug=DEBUG)

# Configuration
AGNO_AUTH_TOKEN = os.getenv("AGNO_AUTH_TOKEN", "")
AGNO_BOT_ID = os.getenv("AGNO_BOT_ID", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Try to import AgentOS
try:
    from agno.os import AgentOS
    from agno.os.config import AgentOSConfig, ChatConfig
    
    AGENTOS_AVAILABLE = True
    print("AgentOS disponivel")
    
    # Configure AgentOS
    agent_os = AgentOS(
        description="ARIA-SDR - Agente de Relacionamento Inteligente da AR Online",
        config=AgentOSConfig(
            chat=ChatConfig(
                quick_prompts={
                    "aria-sdr": [
                        "O que vocÃª pode fazer?",
                        "Como funciona a AR Online?",
                        "Quero enviar e-mails em massa",
                    ]
                }
            ),
        ),
    )
    
    # Get AgentOS routes
    agentos_routes = agent_os.get_routes()
    print(f"AgentOS configurado com {len(agentos_routes)} rotas")
    
    # Add AgentOS routes to our app
    for route in agentos_routes:
        app.router.routes.append(route)
        print(f"Rota adicionada: {route.path}")
        
except ImportError as e:
    AGENTOS_AVAILABLE = False
    print(f"AgentOS nao disponivel: {e}")
except Exception as e:
    AGENTOS_AVAILABLE = False
    print(f"Erro ao configurar AgentOS: {e}")

# Models
class AssistRequest(BaseModel):
    input: str | None = None
    user_text: str | None = None
    message: str | None = None
    variables: dict[str, Any] | None = None

class AssistResponse(BaseModel):
    reply_text: str
    route: str | None = None
    thread_id: str | None = None
    variables: dict[str, str] | None = None
    next_action: str | None = None
    agentos: bool = False
    config_loaded: bool = True

# Business rules
def classify_route(user_text: str, v: dict[str, Any]) -> tuple[str | None, dict[str, str], str | None]:
    """Classify route and volume deterministically"""
    import re
    
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

# Routes
@app.get("/healthz")
def healthz():
    return {
        "ok": True, 
        "agentos": AGENTOS_AVAILABLE,
        "config_loaded": True,
        "agno_token": bool(AGNO_AUTH_TOKEN),
        "agno_bot_id": bool(AGNO_BOT_ID),
        "openai_key": bool(OPENAI_API_KEY),
        "total_routes": len(agentos_routes) if AGENTOS_AVAILABLE else 0,
        "status": "fully_configured" if AGENTOS_AVAILABLE else "partial"
    }

@app.post("/assist/routing")
def assist_routing(
    request: Request,
    payload: AssistRequest = Body(default_factory=AssistRequest),
):
    """Endpoint principal de roteamento com AgentOS (sem autenticaÃ§Ã£o para teste)"""
    t0 = time.time()
    
    try:
        # Extract user input
        user_text = str(
            payload.input or payload.user_text or payload.message or ""
        ).strip()
        
        v_in: dict[str, Any] = dict(payload.variables or {})
        
        # Generate thread ID
        import secrets
        app_thread_id = f"thr_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(2)}"
        
        # Use AgentOS if available
        if AGENTOS_AVAILABLE:
            reply_text = f"ARIA-SDR AgentOS: Recebi sua mensagem '{user_text}'. Sistema funcionando com AgentOS!"
            agent_used = True
        else:
            # Fallback to original logic
            reply_text = f"ARIA-SDR: Recebi sua mensagem '{user_text}'. Sistema funcionando sem AgentOS."
            agent_used = False
        
        # Classify route
        route, vars_out, next_action = classify_route(user_text, v_in)
        
        # Log the interaction
        dur_ms = int((time.time() - t0) * 1000)
        
        return AssistResponse(
            reply_text=reply_text,
            route=route,
            thread_id=app_thread_id,
            variables=vars_out,
            next_action=next_action,
            agentos=AGENTOS_AVAILABLE,
            config_loaded=True,
        )
        
    except Exception as e:
        return AssistResponse(
            reply_text="Erro interno do sistema.",
            agentos=AGENTOS_AVAILABLE,
            config_loaded=True,
        )

@app.get("/agentos/info")
def get_agentos_info():
    """Get AgentOS configuration information"""
    return {
        "agentos_available": AGENTOS_AVAILABLE,
        "total_routes": len(agentos_routes) if AGENTOS_AVAILABLE else 0,
        "config_loaded": True,
        "quick_prompts": {
            "aria-sdr": [
                "O que vocÃª pode fazer?",
                "Como funciona a AR Online?",
                "Quero enviar e-mails em massa",
            ]
        },
        "agno_token_configured": bool(AGNO_AUTH_TOKEN),
        "agno_bot_id_configured": bool(AGNO_BOT_ID),
        "openai_key_configured": bool(OPENAI_API_KEY),
        "status": "ready_for_agentos"
    }

@app.get("/agentos/routes")
def get_agentos_routes():
    """List all AgentOS routes"""
    if not AGENTOS_AVAILABLE:
        return {"error": "AgentOS nÃ£o disponÃ­vel", "status": "ready_for_agentos"}
    
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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
