# main_agno_simple_config.py - IntegraÃ§Ã£o simples com AgentOS
from __future__ import annotations

import os
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI

# Load .env
load_dotenv(find_dotenv(), override=False)

# Create FastAPI app
app = FastAPI(title="ARIA-SDR AgentOS Simple", debug=True)

# Try to import AgentOS
try:
    from agno.os import AgentOS
    from agno.os.config import AgentOSConfig, ChatConfig
    
    AGENTOS_AVAILABLE = True
    print("âœ… AgentOS disponÃ­vel")
    
    # Simple AgentOS configuration
    agent_os = AgentOS(
        description="ARIA-SDR - Agente de Relacionamento Inteligente da AR Online",
        config=AgentOSConfig(
            chat=ChatConfig(
                quick_prompts={
                    "aria-sdr": [
                        "O que vocÃª pode fazer?",
                        "Como funciona a AR Online?",
                        "Quero enviar e-mails em massa",
                        "Qual o preÃ§o para 1500 e-mails?",
                        "Preciso de agendamento",
                    ]
                }
            ),
        ),
    )
    
    # Get AgentOS routes
    agentos_routes = agent_os.get_routes()
    print(f"âœ… AgentOS configurado com {len(agentos_routes)} rotas")
    
    # Add AgentOS routes to our app
    for route in agentos_routes:
        app.router.routes.append(route)
        print(f"âž• Rota adicionada: {route.path}")
        
except ImportError as e:
    AGENTOS_AVAILABLE = False
    print(f"âš ï¸ AgentOS nÃ£o disponÃ­vel: {e}")
except Exception as e:
    AGENTOS_AVAILABLE = False
    print(f"âŒ Erro ao configurar AgentOS: {e}")

@app.get("/healthz")
def healthz():
    return {
        "ok": True, 
        "agentos": AGENTOS_AVAILABLE,
        "config_loaded": True,
        "agno_token": bool(os.getenv("AGNO_AUTH_TOKEN"))
    }

@app.get("/agentos/info")
def get_agentos_info():
    """Get AgentOS configuration information"""
    if not AGENTOS_AVAILABLE:
        return {"error": "AgentOS nÃ£o disponÃ­vel"}
    
    return {
        "agentos_available": AGENTOS_AVAILABLE,
        "total_routes": len(agentos_routes) if AGENTOS_AVAILABLE else 0,
        "config_loaded": True,
        "quick_prompts": {
            "aria-sdr": [
                "O que vocÃª pode fazer?",
                "Como funciona a AR Online?",
                "Quero enviar e-mails em massa",
                "Qual o preÃ§o para 1500 e-mails?",
                "Preciso de agendamento",
            ]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
