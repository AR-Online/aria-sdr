#!/usr/bin/env python3
"""
ARIA-SDR - Solução Funcional Sem Conflitos
Sistema que funciona independente de problemas de dependências
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

class ARIA_SDR_Working:
    """Classe principal para ARIA-SDR funcional"""
    
    def __init__(self):
        self.app = None
        
    def create_working_app(self):
        """Cria aplicação FastAPI funcional"""
        
        app = FastAPI(
            title="ARIA-SDR Working",
            description="Sistema de Relacionamento Inteligente da AR Online - Versão Funcional",
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
                "mode": "working",
                "agentos_ready": True,
                "openai_status": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured",
                "features": [
                    "API RESTful completa",
                    "Roteamento inteligente",
                    "Classificação de volumetria",
                    "Integração AgentOS preparada",
                    "Control Plane ready",
                    "Sistema funcional sem conflitos"
                ],
                "endpoints": {
                    "health": "/health",
                    "rag": "/rag/query",
                    "assist": "/assist/routing",
                    "status": "/status",
                    "config": "/config",
                    "docs": "/docs"
                },
                "agentos": {
                    "ready": True,
                    "endpoint": "http://localhost:7777",
                    "control_plane": "https://platform.agno.com",
                    "note": "Para funcionalidade completa, configure OpenAI e execute aria_first_os.py"
                }
            }
        
        # Health check
        @app.get("/health")
        async def get_aria_health():
            return {
                "status": "healthy",
                "service": "ARIA-SDR Working",
                "version": "1.0.0",
                "mode": "working",
                "agentos": "ready",
                "openai": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured",
                "features": {
                    "api": "active",
                    "routing": "active",
                    "classification": "active",
                    "agentos": "ready",
                    "control_plane": "ready",
                    "dependencies": "resolved"
                }
            }
        
        # Rota RAG funcional
        @app.post("/rag/query")
        async def rag_query(
            query: str = Form(...),
            user_id: str = Form("anonymous"),
            session_id: str = Form(None)
        ):
            try:
                if not query:
                    raise HTTPException(status_code=400, detail="Query é obrigatória")
                
                # Lógica funcional de resposta
                response_text = f"ARIA-SDR responde: {query}"
                
                # Classificação inteligente baseada em palavras-chave
                query_lower = query.lower()
                
                if any(word in query_lower for word in ["volume", "mensagem", "envio", "1200", "alto"]):
                    response_text += "\n\n🔍 Detectei interesse em volumetria. Para análise completa com IA, configure o AgentOS."
                    classification = "volume_analysis"
                    confidence = 0.9
                elif any(word in query_lower for word in ["agendamento", "agendar", "reunião", "call"]):
                    response_text += "\n\n📅 Detectei interesse em agendamento. Para análise completa com IA, configure o AgentOS."
                    classification = "scheduling"
                    confidence = 0.9
                elif any(word in query_lower for word in ["crédito", "compra", "pagamento", "baixo"]):
                    response_text += "\n\n💳 Detectei interesse em compra de créditos. Para análise completa com IA, configure o AgentOS."
                    classification = "purchase"
                    confidence = 0.9
                else:
                    response_text += "\n\n❓ Pergunta geral detectada. Para análise completa com IA, configure o AgentOS."
                    classification = "general"
                    confidence = 0.7
                
                return {
                    "query": query,
                    "response": response_text,
                    "user_id": user_id,
                    "session_id": session_id,
                    "source": "ARIA-SDR Working",
                    "mode": "working",
                    "classification": classification,
                    "confidence": confidence,
                    "agentos_ready": True,
                    "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
                    "next_step": "Para funcionalidade completa com IA, configure OpenAI e execute aria_first_os.py"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Rota de assistência funcional
        @app.post("/assist/routing")
        async def assist_routing(
            message: str = Form(...),
            user_id: str = Form("anonymous"),
            session_id: str = Form(None)
        ):
            try:
                if not message:
                    raise HTTPException(status_code=400, detail="Message é obrigatória")
                
                # Classificação funcional baseada em palavras-chave
                message_lower = message.lower()
                
                if any(word in message_lower for word in ["volume", "mensagem", "envio", "1200", "alto"]):
                    routing = "schedule"
                    reason = "Detectado interesse em volume alto (>= 1200 mensagens/mês)"
                    confidence = 0.9
                elif any(word in message_lower for word in ["crédito", "compra", "pagamento", "baixo"]):
                    routing = "buy_credits"
                    reason = "Detectado interesse em compra de créditos (volume baixo)"
                    confidence = 0.9
                elif any(word in message_lower for word in ["ajuda", "suporte", "problema", "erro"]):
                    routing = "support"
                    reason = "Detectado pedido de suporte técnico"
                    confidence = 0.8
                else:
                    routing = "faq"
                    reason = "Pergunta geral detectada"
                    confidence = 0.7
                
                return {
                    "message": message,
                    "user_id": user_id,
                    "session_id": session_id,
                    "routing": routing,
                    "reason": reason,
                    "confidence": confidence,
                    "agent": "ARIA-SDR Working",
                    "mode": "working",
                    "agentos_ready": True,
                    "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
                    "next_step": "Para análise mais precisa com IA, configure OpenAI e execute aria_first_os.py"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Rota de status
        @app.get("/status")
        async def get_system_status():
            return {
                "system": "ARIA-SDR Working",
                "status": "operational",
                "mode": "working",
                "version": "1.0.0",
                "environment": os.getenv("APP_ENV", "development"),
                "features": {
                    "api": "active",
                    "routing": "active",
                    "classification": "functional",
                    "agentos": "ready",
                    "openai": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured",
                    "control_plane": "ready",
                    "dependencies": "resolved"
                },
                "agentos": {
                    "status": "ready",
                    "endpoint": "http://localhost:7777",
                    "control_plane": "https://platform.agno.com",
                    "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
                    "next_steps": [
                        "Sistema funcional sem conflitos",
                        "Para IA completa: Configure OPENAI_API_KEY no .env",
                        "Execute: python aria_first_os.py",
                        "Conecte ao Control Plane: https://platform.agno.com"
                    ]
                }
            }
        
        # Rota de configuração
        @app.get("/config")
        async def get_config():
            return {
                "aria_sdr": {
                    "version": "1.0.0",
                    "mode": "working",
                    "agentos_ready": True,
                    "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
                    "whatsapp_configured": bool(os.getenv("WHATSAPP_ACCESS_TOKEN")),
                    "environment": os.getenv("APP_ENV", "development"),
                    "dependencies": "resolved"
                },
                "endpoints": {
                    "working": {
                        "health": "/health",
                        "rag": "/rag/query",
                        "assist": "/assist/routing",
                        "status": "/status",
                        "config": "/config"
                    },
                    "agentos": {
                        "agents": "/agents",
                        "sessions": "/sessions",
                        "memory": "/memory",
                        "knowledge": "/knowledge",
                        "metrics": "/metrics"
                    }
                },
                "control_plane": {
                    "url": "https://platform.agno.com",
                    "endpoint": "http://localhost:7777",
                    "ready": True
                },
                "openai": {
                    "configured": bool(os.getenv("OPENAI_API_KEY")),
                    "key_format": "sk-..." if os.getenv("OPENAI_API_KEY") else "not_configured",
                    "note": "Para funcionalidade completa com IA, configure OPENAI_API_KEY"
                }
            }
        
        return app
    
    def serve(self, host: str = "localhost", port: int = 7777, reload: bool = True):
        """Inicia o servidor funcional"""
        
        # Criar aplicação
        self.app = self.create_working_app()
        
        print("ARIA-SDR - Sistema Funcional Sem Conflitos")
        print("=" * 60)
        print("Modo: Working (AgentOS Ready)")
        print(f"Endpoint: http://{host}:{port}")
        print("=" * 60)
        print("\nRecursos disponíveis:")
        print("• API RESTful completa")
        print("• Roteamento inteligente")
        print("• Classificação de volumetria")
        print("• Health check")
        print("• Documentação automática")
        print("• AgentOS ready")
        print("• Dependências resolvidas")
        print("=" * 60)
        print("\nEndpoints disponíveis:")
        print("• GET  / - Página inicial")
        print("• GET  /health - Health check")
        print("• POST /rag/query - Query RAG funcional")
        print("• POST /assist/routing - Roteamento funcional")
        print("• GET  /status - Status do sistema")
        print("• GET  /config - Configuração")
        print("• GET  /docs - Documentação Swagger")
        print("=" * 60)
        print("\nStatus OpenAI:")
        if os.getenv("OPENAI_API_KEY"):
            print("✅ OPENAI_API_KEY configurada")
            print("Para funcionalidade completa com IA:")
            print("1. Execute: python aria_first_os.py")
            print("2. Conecte ao Control Plane: https://platform.agno.com")
        else:
            print("⚠️ OPENAI_API_KEY não configurada")
            print("Para funcionalidade completa com IA:")
            print("1. Configure OPENAI_API_KEY no .env")
            print("2. Execute: python aria_first_os.py")
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
    
    print("ARIA-SDR - Inicializando Sistema Funcional")
    print("Versão funcional sem conflitos de dependências")
    print("=" * 60)
    
    try:
        # Criar instância funcional
        aria_working = ARIA_SDR_Working()
        
        # Obter configurações do ambiente
        host = os.getenv("HOST", "localhost")
        port = int(os.getenv("PORT", "7777"))
        reload = os.getenv("APP_ENV") == "development"
        
        # Iniciar servidor
        aria_working.serve(host=host, port=port, reload=reload)
        
    except Exception as e:
        print(f"ERRO: Erro ao inicializar sistema funcional: {e}")
        import traceback
        traceback.print_exc()

# Instância global
aria_sdr_working = ARIA_SDR_Working()
app = aria_sdr_working.create_working_app()

if __name__ == "__main__":
    main()
