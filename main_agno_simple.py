# main_agno_simple.py - ARIA-SDR simples para Agno
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Optional
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Create FastAPI app
app = FastAPI(title="ARIA-SDR Simple", version="1.0.0")

# Configuration
AGNO_AUTH_TOKEN = os.getenv("AGNO_AUTH_TOKEN", "")
AGNO_BOT_ID = os.getenv("AGNO_BOT_ID", "")

# Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

# Routes
@app.get("/")
def root():
    """Root endpoint for Agno health check"""
    return {
        "message": "ARIA-SDR is running",
        "status": "active",
        "version": "1.0.0",
        "agno_configured": bool(AGNO_AUTH_TOKEN and AGNO_BOT_ID)
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agno_token": bool(AGNO_AUTH_TOKEN),
        "agno_bot_id": bool(AGNO_BOT_ID)
    }

@app.post("/chat")
def chat(request: ChatRequest):
    """Main chat endpoint for Agno"""
    message = request.message.lower()
    
    # Simple responses based on message content
    if "enviar" in message or "email" in message:
        response = "Para enviar e-mails em massa, vocÃª pode usar nossa plataforma AR Online. Qual o volume de envios que vocÃª precisa?"
    elif "preÃ§o" in message or "valor" in message:
        response = "Os preÃ§os variam conforme o volume. Para volumes acima de 1200 mensagens/mÃªs, recomendamos agendamento. Para volumes menores, vocÃª pode comprar crÃ©ditos na loja."
    elif "agendamento" in message:
        response = "Para agendamento de envios em massa, vocÃª precisa de um volume alto (acima de 1200 mensagens/mÃªs). Posso encaminhar vocÃª para nosso time comercial."
    elif "recebimento" in message or "recebi" in message:
        response = "Para dÃºvidas sobre recebimento de e-mails, posso ajudar com informaÃ§Ãµes sobre abertura, cliques e relatÃ³rios de entrega."
    else:
        response = "OlÃ¡! Sou a ARIA, Agente de Relacionamento Inteligente da AR Online. Como posso ajudar vocÃª hoje?"
    
    return ChatResponse(response=response)

@app.get("/agno/status")
def agno_status():
    """Agno specific status endpoint"""
    return {
        "status": "active",
        "message": "ARIA-SDR is ready for Agno",
        "agno_token_configured": bool(AGNO_AUTH_TOKEN),
        "agno_bot_id_configured": bool(AGNO_BOT_ID)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
