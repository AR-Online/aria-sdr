#!/usr/bin/env python3
"""
ARIA-SDR - Implementação Completa com AgentOS API
Baseado na documentação oficial: https://docs.agno.com/agent-os/api
"""

import os
import sys
import json
from textwrap import dedent
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Imports do Agno
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.db.postgres import PostgresDb
from agno.memory.manager import MemoryManager
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.os.app import AgentOS
from agno.os.config import (
    AgentOSConfig,
    ChatConfig,
    DatabaseConfig,
    MemoryConfig,
    MemoryDomainConfig,
)
from agno.os.interfaces.whatsapp import Whatsapp
from agno.tools.googlesearch import GoogleSearchTools

# Carregar variáveis de ambiente
load_dotenv()

class ARIA_SDR_API:
    """Classe principal para ARIA-SDR com API completa do AgentOS"""
    
    def __init__(self):
        self.agent_os = None
        self.aria_agent = None
        self.app = None
        self.security_key = os.getenv("AGENTOS_SECURITY_KEY")
        
    def create_database(self):
        """Cria banco de dados baseado no ambiente"""
        env = os.getenv("APP_ENV", "development")
        
        if env == "production":
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise ValueError("DATABASE_URL é obrigatória em produção")
            return PostgresDb(db_url=db_url)
        else:
            return SqliteDb(db_file="tmp/aria_api.db")
    
    def create_model(self):
        """Cria modelo baseado na configuração"""
        model_provider = os.getenv("MODEL_PROVIDER", "openai")
        model_id = os.getenv("MODEL_ID", "gpt-4o-mini")
        
        if model_provider == "openai":
            return OpenAIChat(id=model_id)
        elif model_provider == "google":
            return Gemini(id=model_id)
        else:
            return OpenAIChat(id="gpt-4o-mini")
    
    def create_aria_agent(self):
        """Cria o agente ARIA-SDR principal"""
        
        # Componentes base
        db = self.create_database()
        model = self.create_model()
        
        # Gerenciador de memória
        memory_manager = MemoryManager(
            memory_capture_instructions=dedent("""
                Collect User's name,
                Collect Information about user's passion and hobbies,
                Collect Information about the users likes and dislikes,
                Collect information about what the user is doing with their life right now,
                Collect information about their business needs and volume requirements
            """),
            model=model,
        )
        
        # Instruções do agente
        instructions = dedent("""
            Você é a ARIA, Agente de Relacionamento Inteligente da AR Online.
            
            Suas responsabilidades:
            1. Atender clientes via WhatsApp e chat web
            2. Classificar volumetria de envios (alto/baixo volume)
            3. Roteamento inteligente para FAQ, agendamento ou loja
            4. Responder em português brasileiro de forma cordial e objetiva
            
            Regras de negócio:
            - Volume alto: >= 1200 mensagens/mês → Agendamento
            - Volume baixo: < 1200 mensagens/mês → Loja
            - Use contexto fornecido quando disponível
            - Se não souber algo, ofereça encaminhar ao time
            
            Sempre seja cordial, objetivo e profissional.
        """)
        
        # Criar agente
        self.aria_agent = Agent(
            id="aria-sdr-agent",
            name="ARIA-SDR",
            model=model,
            tools=[GoogleSearchTools()],
            db=db,
            memory_manager=memory_manager,
            enable_agentic_memory=True,
            add_history_to_context=True,
            num_history_runs=3,
            add_datetime_to_context=True,
            markdown=True,
            instructions=instructions,
            debug_mode=os.getenv("APP_ENV") == "development",
        )
        
        return self.aria_agent
    
    def create_agentos_config(self):
        """Cria configuração otimizada do AgentOS"""
        
        return AgentOSConfig(
            chat=ChatConfig(
                quick_prompts={
                    "aria-sdr-agent": [
                        "Qual é o seu volume mensal de mensagens?",
                        "Precisa de agendamento ou compra de créditos?",
                        "Como posso ajudar com seu negócio?",
                        "Conte-me sobre suas necessidades de comunicação",
                        "Qual é o seu principal desafio atual?"
                    ]
                }
            ),
            memory=MemoryConfig(
                dbs=[
                    DatabaseConfig(
                        db_id="aria-sdr-db",
                        domain_config=MemoryDomainConfig(
                            display_name="Memórias dos usuários ARIA-SDR"
                        )
                    )
                ]
            )
        )
    
    def create_custom_app(self):
        """Cria aplicação FastAPI customizada com rotas ARIA-SDR"""
        
        app = FastAPI(
            title="ARIA-SDR API",
            description="Sistema de Relacionamento Inteligente da AR Online com AgentOS API",
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
        
        # Autenticação (se configurada)
        security = HTTPBearer(auto_error=False)
        
        async def verify_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
            if self.security_key and not credentials:
                raise HTTPException(status_code=401, detail="Token de autorização necessário")
            
            if self.security_key and credentials.credentials != self.security_key:
                raise HTTPException(status_code=401, detail="Token inválido")
            
            return credentials
        
        # Rota principal customizada
        @app.get("/")
        async def get_aria_home():
            return {
                "message": "ARIA-SDR - Sistema de Relacionamento Inteligente",
                "version": "1.0.0",
                "status": "active",
                "agentos_api": "enabled",
                "features": [
                    "Chat inteligente via API",
                    "Classificação de volumetria",
                    "Roteamento automático",
                    "Memória persistente",
                    "Integração WhatsApp",
                    "API RESTful completa"
                ],
                "endpoints": {
                    "health": "/health",
                    "rag": "/rag/query",
                    "assist": "/assist/routing",
                    "agentos_api": "/agents/aria-sdr-agent/runs",
                    "docs": "/docs",
                    "sessions": "/sessions"
                }
            }
        
        # Health check customizado
        @app.get("/health")
        async def get_aria_health():
            return {
                "status": "healthy",
                "service": "ARIA-SDR",
                "version": "1.0.0",
                "agentos_api": "active",
                "authentication": "enabled" if self.security_key else "disabled",
                "features": {
                    "chat": "active",
                    "memory": "active",
                    "whatsapp": "active" if os.getenv("WHATSAPP_ACCESS_TOKEN") else "inactive",
                    "google_search": "active",
                    "api_endpoints": "active"
                }
            }
        
        # Rota RAG existente (preservada)
        @app.post("/rag/query")
        async def rag_query(
            query: str = Form(...),
            user_id: str = Form("anonymous"),
            session_id: Optional[str] = Form(None),
            dependencies: Optional[str] = Form(None)
        ):
            try:
                if not query:
                    raise HTTPException(status_code=400, detail="Query é obrigatória")
                
                # Processar dependências se fornecidas
                deps = {}
                if dependencies:
                    try:
                        deps = json.loads(dependencies)
                    except json.JSONDecodeError:
                        raise HTTPException(status_code=400, detail="Dependencies deve ser JSON válido")
                
                # Usar agente ARIA para processar query RAG
                response = self.aria_agent.run(query, dependencies=deps)
                
                return {
                    "query": query,
                    "response": response.content,
                    "user_id": user_id,
                    "session_id": session_id,
                    "source": "ARIA-SDR Agent",
                    "dependencies": deps,
                    "timestamp": response.created_at if hasattr(response, 'created_at') else None
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Rota de assistência existente (preservada)
        @app.post("/assist/routing")
        async def assist_routing(
            message: str = Form(...),
            user_id: str = Form("anonymous"),
            session_id: Optional[str] = Form(None),
            dependencies: Optional[str] = Form(None)
        ):
            try:
                if not message:
                    raise HTTPException(status_code=400, detail="Message é obrigatória")
                
                # Processar dependências se fornecidas
                deps = {}
                if dependencies:
                    try:
                        deps = json.loads(dependencies)
                    except json.JSONDecodeError:
                        raise HTTPException(status_code=400, detail="Dependencies deve ser JSON válido")
                
                # Usar agente ARIA para roteamento inteligente
                routing_prompt = f"""
                Analise a seguinte mensagem e determine o roteamento:
                Mensagem: {message}
                Usuário: {user_id}
                
                Classifique como:
                - "faq" para perguntas gerais
                - "schedule" para agendamento (volume alto)
                - "buy_credits" para compra de créditos (volume baixo)
                - "support" para suporte técnico
                
                Responda apenas com a classificação.
                """
                
                response = self.aria_agent.run(routing_prompt, dependencies=deps)
                
                return {
                    "message": message,
                    "user_id": user_id,
                    "session_id": session_id,
                    "routing": response.content.strip().lower(),
                    "agent": "ARIA-SDR",
                    "dependencies": deps,
                    "timestamp": response.created_at if hasattr(response, 'created_at') else None
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Rota de status do sistema
        @app.get("/status")
        async def get_system_status():
            return {
                "system": "ARIA-SDR",
                "status": "operational",
                "agentos_api": "active",
                "agent_id": self.aria_agent.id if self.aria_agent else "not_initialized",
                "agent_name": self.aria_agent.name if self.aria_agent else "not_initialized",
                "model": str(self.aria_agent.model) if self.aria_agent else "not_initialized",
                "tools": len(self.aria_agent.tools) if self.aria_agent else 0,
                "environment": os.getenv("APP_ENV", "development"),
                "authentication": "enabled" if self.security_key else "disabled"
            }
        
        # Rota para listar agentes disponíveis
        @app.get("/agents")
        async def list_agents():
            return {
                "agents": [
                    {
                        "id": self.aria_agent.id,
                        "name": self.aria_agent.name,
                        "model": str(self.aria_agent.model),
                        "tools": [str(tool) for tool in self.aria_agent.tools],
                        "status": "active"
                    }
                ]
            }
        
        # Rota para executar agente via API (compatível com AgentOS API)
        @app.post("/agents/{agent_id}/runs")
        async def run_agent(
            agent_id: str,
            message: str = Form(...),
            user_id: str = Form("anonymous"),
            session_id: Optional[str] = Form(None),
            stream: bool = Form(False),
            dependencies: Optional[str] = Form(None),
            auth: Optional[HTTPAuthorizationCredentials] = Depends(verify_auth)
        ):
            try:
                if agent_id != "aria-sdr-agent":
                    raise HTTPException(status_code=404, detail="Agente não encontrado")
                
                if not message:
                    raise HTTPException(status_code=400, detail="Message é obrigatória")
                
                # Processar dependências se fornecidas
                deps = {}
                if dependencies:
                    try:
                        deps = json.loads(dependencies)
                    except json.JSONDecodeError:
                        raise HTTPException(status_code=400, detail="Dependencies deve ser JSON válido")
                
                # Executar agente
                response = self.aria_agent.run(message, dependencies=deps)
                
                result = {
                    "agent_id": agent_id,
                    "message": message,
                    "response": response.content,
                    "user_id": user_id,
                    "session_id": session_id,
                    "dependencies": deps,
                    "timestamp": response.created_at if hasattr(response, 'created_at') else None
                }
                
                if stream:
                    # Implementar streaming se necessário
                    return StreamingResponse(
                        iter([json.dumps(result)]),
                        media_type="application/json"
                    )
                else:
                    return result
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        return app
    
    def create_interfaces(self):
        """Cria interfaces baseadas na configuração"""
        interfaces = []
        
        # Interface WhatsApp
        whatsapp_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        if whatsapp_token:
            whatsapp_interface = Whatsapp(agent=self.aria_agent)
            interfaces.append(whatsapp_interface)
            print("OK: Interface WhatsApp configurada")
        else:
            print("AVISO: WhatsApp não configurado - apenas chat web disponível")
        
        return interfaces
    
    def create_integrated_agentos(self):
        """Cria AgentOS integrado com aplicação customizada"""
        
        # Criar agente
        self.create_aria_agent()
        
        # Criar aplicação customizada
        custom_app = self.create_custom_app()
        
        # Criar interfaces
        interfaces = self.create_interfaces()
        
        # Criar configuração
        config = self.create_agentos_config()
        
        # Criar AgentOS com aplicação customizada
        self.agent_os = AgentOS(
            id="aria-sdr-api",
            name="ARIA-SDR API",
            description="Sistema ARIA-SDR com API completa do AgentOS",
            version="1.0.0",
            agents=[self.aria_agent],
            interfaces=interfaces,
            config=config,
            base_app=custom_app,
            on_route_conflict="preserve_base_app",  # Preservar nossas rotas customizadas
            telemetry=True,
            enable_mcp_server=False,
        )
        
        return self.agent_os
    
    def get_app(self):
        """Obtém o app FastAPI integrado"""
        if not self.agent_os:
            self.create_integrated_agentos()
        return self.agent_os.get_app()
    
    def serve(self, host: str = "localhost", port: int = 7777, reload: bool = True):
        """Inicia o servidor integrado"""
        
        if not self.agent_os:
            self.create_integrated_agentos()
        
        print("ARIA-SDR - Sistema com API Completa do AgentOS")
        print("=" * 60)
        print(f"Agente: {self.aria_agent.name} (ID: {self.aria_agent.id})")
        print(f"Modelo: {self.aria_agent.model}")
        print(f"Ferramentas: {len(self.aria_agent.tools)}")
        print(f"Interfaces: {len(self.agent_os.interfaces)}")
        print(f"Endpoint: http://{host}:{port}")
        print("=" * 60)
        print("\nRotas customizadas preservadas:")
        print("• GET  / - Página inicial ARIA-SDR")
        print("• GET  /health - Health check customizado")
        print("• POST /rag/query - Query RAG")
        print("• POST /assist/routing - Roteamento inteligente")
        print("• GET  /status - Status do sistema")
        print("• GET  /agents - Listar agentes")
        print("=" * 60)
        print("\nAPI AgentOS disponível:")
        print("• POST /agents/aria-sdr-agent/runs - Executar agente")
        print("• GET  /sessions - Gerenciar sessões")
        print("• GET  /memory - Gerenciar memória")
        print("• GET  /knowledge - Gerenciar conhecimento")
        print("• GET  /metrics - Métricas do sistema")
        print("=" * 60)
        print("\nExemplo de uso da API:")
        print(f"curl -X POST 'http://{host}:{port}/agents/aria-sdr-agent/runs' \\")
        print("  -H 'Content-Type: application/x-www-form-urlencoded' \\")
        print("  -d 'message=Qual é o seu volume mensal?' \\")
        print("  -d 'user_id=usuario@exemplo.com'")
        print("=" * 60)
        print("\nPara conectar ao Control Plane:")
        print(f"1. Acesse: https://platform.agno.com")
        print(f"2. Adicione novo OS: http://{host}:{port}")
        print(f"3. Nome: ARIA-SDR API")
        print("=" * 60)
        
        # Iniciar servidor
        self.agent_os.serve(
            app="aria_sdr_api:app",
            host=host,
            port=port,
            reload=reload
        )

def main():
    """Função principal"""
    
    print("ARIA-SDR - Inicializando Sistema com API Completa")
    print("Integração completa com AgentOS API")
    print("=" * 60)
    
    try:
        # Criar instância integrada
        aria_api = ARIA_SDR_API()
        
        # Obter configurações do ambiente
        host = os.getenv("HOST", "localhost")
        port = int(os.getenv("PORT", "7777"))
        reload = os.getenv("APP_ENV") == "development"
        
        # Iniciar servidor
        aria_api.serve(host=host, port=port, reload=reload)
        
    except Exception as e:
        print(f"ERRO: Erro ao inicializar sistema com API: {e}")
        import traceback
        traceback.print_exc()

# Instância global para uso com AgentOS
aria_sdr_api = ARIA_SDR_API()
app = aria_sdr_api.get_app()

if __name__ == "__main__":
    main()
