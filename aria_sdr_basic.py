#!/usr/bin/env python3
"""
ARIA-SDR - Implementação Funcional Básica
Sistema funcional sem dependências externas
"""

import os
import sys
from textwrap import dedent
from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class ARIA_SDR_Basic:
    """Classe principal para ARIA-SDR básico"""
    
    def __init__(self):
        self.app = None
        
    def create_basic_app(self):
        """Cria aplicação FastAPI básica"""
        
        app = FastAPI(
            title="ARIA-SDR Basic",
            description="Sistema de Relacionamento Inteligente da AR Online - Versão Básica",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Rota principal
        @app.get("/")
        async def get_aria_home():
            return {
                "message": "ARIA-SDR - Sistema de Relacionamento Inteligente",
                "version": "1.0.0",
                "status": "active",
                "mode": "basic",
                "features": [
                    "API RESTful básica",
                    "Roteamento inteligente",
                    "Classificação de volumetria",
                    "Integração preparada para AgentOS"
                ],
                "endpoints": {
                    "health": "/health",
                    "rag": "/rag/query",
                    "assist": "/assist/routing",
                    "status": "/status",
                    "docs": "/docs"
                }
            }
        
        # Health check
        @app.get("/health")
        async def get_aria_health():
            return {
                "status": "healthy",
                "service": "ARIA-SDR Basic",
                "version": "1.0.0",
                "mode": "basic",
                "features": {
                    "api": "active",
                    "routing": "active",
                    "classification": "active",
                    "agentos": "prepared"
                }
            }
        
        # Rota RAG básica
        @app.post("/rag/query")
        async def rag_query(
            query: str = Form(...),
            user_id: str = Form("anonymous"),
            session_id: str = Form(None)
        ):
            try:
                if not query:
                    raise HTTPException(status_code=400, detail="Query é obrigatória")
                
                # Lógica básica de resposta
                response_text = f"Resposta básica para: {query}"
                
                # Classificação simples baseada em palavras-chave
                if any(word in query.lower() for word in ["volume", "mensagem", "envio"]):
                    response_text += "\n\nDetectei interesse em volumetria. Para análise completa, configure o AgentOS."
                elif any(word in query.lower() for word in ["agendamento", "agendar", "reunião"]):
                    response_text += "\n\nDetectei interesse em agendamento. Para análise completa, configure o AgentOS."
                elif any(word in query.lower() for word in ["crédito", "compra", "pagamento"]):
                    response_text += "\n\nDetectei interesse em compra de créditos. Para análise completa, configure o AgentOS."
                
                return {
                    "query": query,
                    "response": response_text,
                    "user_id": user_id,
                    "session_id": session_id,
                    "source": "ARIA-SDR Basic",
                    "mode": "basic",
                    "note": "Para funcionalidade completa, configure OpenAI e AgentOS"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Rota de assistência básica
        @app.post("/assist/routing")
        async def assist_routing(
            message: str = Form(...),
            user_id: str = Form("anonymous"),
            session_id: str = Form(None)
        ):
            try:
                if not message:
                    raise HTTPException(status_code=400, detail="Message é obrigatória")
                
                # Classificação básica baseada em palavras-chave
                message_lower = message.lower()
                
                if any(word in message_lower for word in ["volume", "mensagem", "envio", "1200", "alto"]):
                    routing = "schedule"
                    reason = "Detectado interesse em volume alto"
                elif any(word in message_lower for word in ["crédito", "compra", "pagamento", "baixo"]):
                    routing = "buy_credits"
                    reason = "Detectado interesse em compra de créditos"
                elif any(word in message_lower for word in ["ajuda", "suporte", "problema", "erro"]):
                    routing = "support"
                    reason = "Detectado pedido de suporte"
                else:
                    routing = "faq"
                    reason = "Pergunta geral detectada"
                
                return {
                    "message": message,
                    "user_id": user_id,
                    "session_id": session_id,
                    "routing": routing,
                    "reason": reason,
                    "agent": "ARIA-SDR Basic",
                    "mode": "basic",
                    "note": "Para análise mais precisa, configure OpenAI e AgentOS"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Rota de status
        @app.get("/status")
        async def get_system_status():
            return {
                "system": "ARIA-SDR Basic",
                "status": "operational",
                "mode": "basic",
                "version": "1.0.0",
                "environment": os.getenv("APP_ENV", "development"),
                "features": {
                    "api": "active",
                    "routing": "active",
                    "classification": "basic",
                    "agentos": "not_configured",
                    "openai": "not_configured"
                },
                "next_steps": [
                    "Configure OPENAI_API_KEY no .env",
                    "Execute: python aria_sdr_api.py",
                    "Conecte ao Control Plane: https://platform.agno.com"
                ]
            }
        
        # Rota de configuração
        @app.get("/config")
        async def get_config():
            return {
                "aria_sdr": {
                    "version": "1.0.0",
                    "mode": "basic",
                    "agentos_ready": False,
                    "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
                    "whatsapp_configured": bool(os.getenv("WHATSAPP_ACCESS_TOKEN")),
                    "environment": os.getenv("APP_ENV", "development")
                },
                "endpoints": {
                    "basic": {
                        "health": "/health",
                        "rag": "/rag/query",
                        "assist": "/assist/routing",
                        "status": "/status"
                    },
                    "agentos": {
                        "agents": "/agents",
                        "sessions": "/sessions",
                        "memory": "/memory",
                        "knowledge": "/knowledge",
                        "metrics": "/metrics"
                    }
                }
            }
        
        return app
    
    def serve(self, host: str = "localhost", port: int = 7777, reload: bool = True):
        """Inicia o servidor básico"""
        
        # Criar aplicação
        self.app = self.create_basic_app()
        
        print("ARIA-SDR - Sistema Básico Funcional")
        print("=" * 60)
        print("Modo: Básico (sem AgentOS)")
        print(f"Endpoint: http://{host}:{port}")
        print("=" * 60)
        print("\nRecursos disponíveis:")
        print("• API RESTful básica")
        print("• Roteamento inteligente simples")
        print("• Classificação de volumetria")
        print("• Health check")
        print("• Documentação automática")
        print("=" * 60)
        print("\nEndpoints disponíveis:")
        print("• GET  / - Página inicial")
        print("• GET  /health - Health check")
        print("• POST /rag/query - Query RAG básica")
        print("• POST /assist/routing - Roteamento básico")
        print("• GET  /status - Status do sistema")
        print("• GET  /config - Configuração")
        print("• GET  /docs - Documentação Swagger")
        print("=" * 60)
        print("\nPara funcionalidade completa:")
        print("1. Configure OPENAI_API_KEY no .env")
        print("2. Execute: python aria_sdr_api.py")
        print("3. Conecte ao Control Plane: https://platform.agno.com")
        print("=" * 60)
        
        # Iniciar servidor
        import uvicorn
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            reload=reload
        )

def main():
    """Função principal"""
    
    print("ARIA-SDR - Inicializando Sistema Básico")
    print("Versão funcional sem dependências externas")
    print("=" * 60)
    
    try:
        # Criar instância básica
        aria_basic = ARIA_SDR_Basic()
        
        # Obter configurações do ambiente
        host = os.getenv("HOST", "localhost")
        port = int(os.getenv("PORT", "7777"))
        reload = os.getenv("APP_ENV") == "development"
        
        # Iniciar servidor
        aria_basic.serve(host=host, port=port, reload=reload)
        
    except Exception as e:
        print(f"ERRO: Erro ao inicializar sistema básico: {e}")
        import traceback
        traceback.print_exc()

# Instância global
aria_sdr_basic = ARIA_SDR_Basic()
app = aria_sdr_basic.create_basic_app()

if __name__ == "__main__":
    main()
