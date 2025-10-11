# main_agno_compatible.py - ARIA-SDR compatÃ­vel com Agno sem AgentOS
from fastapi import FastAPI, Form, Request
from pydantic import BaseModel
from typing import Any, Optional
import os
import json
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Create FastAPI app
app = FastAPI(title="ARIA-SDR Compatible", version="1.0.0")

# Configuration
AGNO_AUTH_TOKEN = os.getenv("AGNO_AUTH_TOKEN", "")
AGNO_BOT_ID = os.getenv("AGNO_BOT_ID", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

print("ARIA-SDR Compatible iniciado!")

# Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    response: str
    status: str = "success"
    session_id: Optional[str] = None

# Business logic
def classify_route(user_text: str) -> tuple[str, str]:
    """Classify route and volume deterministically"""
    import re
    
    t = (user_text or "").lower()
    route = "geral"
    action = "info"
    
    if any(k in t for k in ["recebi", "receb", "chegou", "abriu", "abertura", "confirmacao de leitura"]):
        route = "recebimento"
        action = "relatorio"
    elif any(k in t for k in ["enviar", "envio", "mandar", "disparar", "disparo", "quero enviar"]):
        route = "envio"
        
        # Check volume
        vol_src = t
        n: int | None = None
        m = re.findall(r"\d{1,3}(?:[\.,]\d{3})+|\d+", vol_src)
        if m:
            digits = re.sub(r"[^\d]", "", m[-1])
            if digits:
                n = int(digits)

        kw_high = re.search(r"(alto volume|grande volume|massivo|lote|mil|1k|1000\+|acima de|>\s*1000)", vol_src)

        if n is not None:
            is_high = n >= 1200
        else:
            is_high = bool(kw_high)

        action = "schedule" if is_high else "buy_credits"
    
    return route, action

def generate_response(user_text: str) -> str:
    """Generate ARIA response"""
    route, action = classify_route(user_text)
    
    if route == "envio":
        if action == "schedule":
            return "Para envios em massa com alto volume (acima de 1200 mensagens/mÃªs), recomendamos agendamento. Posso encaminhar vocÃª para nosso time comercial para discutir as melhores opÃ§Ãµes."
        else:
            return "Para envios em massa com baixo volume (abaixo de 1200 mensagens/mÃªs), vocÃª pode comprar crÃ©ditos na nossa loja. Qual o volume aproximado que vocÃª precisa?"
    elif route == "recebimento":
        return "Para dÃºvidas sobre recebimento de e-mails, posso ajudar com informaÃ§Ãµes sobre abertura, cliques e relatÃ³rios de entrega. O que especificamente vocÃª gostaria de saber?"
    else:
        return "OlÃ¡! Sou a ARIA, Agente de Relacionamento Inteligente da AR Online. Como posso ajudar vocÃª hoje? Posso auxiliar com envios em massa, recebimento de e-mails e outras funcionalidades da plataforma."

# Routes
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "ARIA-SDR Compatible is running",
        "status": "active",
        "version": "1.0.0",
        "agno_configured": bool(AGNO_AUTH_TOKEN and AGNO_BOT_ID)
    }

@app.get("/agents")
def get_agents():
    """List agents endpoint"""
    return {
        "agents": [
            {
                "id": "aria-sdr-agent",
                "name": "ARIA-SDR",
                "description": "Agente de Relacionamento Inteligente da AR Online",
                "status": "active"
            }
        ]
    }

@app.post("/agents/aria-sdr-agent/runs")
def run_agent(
    message: str = Form(...),
    session_id: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    stream: Optional[bool] = Form(False)
):
    """Run agent endpoint conforme documentaÃ§Ã£o Agno"""
    try:
        response_text = generate_response(message)
        
        return {
            "response": response_text,
            "status": "success",
            "session_id": session_id or "default_session",
            "agent_id": "aria-sdr-agent",
            "user_id": user_id
        }
    except Exception as e:
        return {
            "response": "Desculpe, ocorreu um erro ao processar sua mensagem.",
            "status": "error",
            "error": str(e)
        }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agno_token": bool(AGNO_AUTH_TOKEN),
        "agno_bot_id": bool(AGNO_BOT_ID),
        "openai_key": bool(OPENAI_API_KEY)
    }

@app.get("/agno/status")
def agno_status():
    """Agno specific status endpoint"""
    return {
        "status": "active",
        "message": "ARIA-SDR is ready for Agno",
        "agentos_compatible": True,
        "endpoints": {
            "agents": "/agents",
            "run_agent": "/agents/aria-sdr-agent/runs",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
